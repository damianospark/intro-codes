from icecream import ic
from typing import List
from fastapi import FastAPI, Body
import networkx as nx
import osmnx as ox
from pydantic import BaseModel
import requests
import urllib
# from pyproj import Proj, transform
import numpy as np
import pandas as pd
import io
import re
import json
from networkx import DiGraph

from vrpy import VehicleRoutingProblem
# from cplex import Cplex
import logging
import sys
import openrouteservice
from openrouteservice import convert
import polyline
import folium
from typing import List

from fastapi.middleware.cors import CORSMiddleware


import numpy as np
from shapely.geometry import MultiPoint
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

import datetime
import os

# cplex = Cplex()
# cplex.set_log_stream(None)
# cplex.set_error_stream(None)
# cplex.set_warning_stream(None)
# cplex.set_results_stream(None)


ox.config(log_console=True, use_cache=True)

app = FastAPI()
# filepath='./서울_경기일부_그래프.graphml'
# G = ox.load_graphml(filepath)
# m1 = ox.plot_graph_folium(G, popup_attribe="name", weight=1, color="#8b0000")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:50002",
    "http://localhost:51002",
    "http://cleverize.life:50002",
    "http://211.184.228.215:51002",
    "http://localhost:50001",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:50002",
    "http://127.0.0.1:51002",
    "http://211.208.171.207:50002",
    "https://211.208.171.207:50002",
    "http://127.0.0.1:3000",
    "http://cleango.surge.sh",
    "https://cleango.surge.sh",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def abs_one(vn):
    return int(vn / vn if vn < 0 else vn)


def getLatLng(addr):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'KakaoAK {}'.format('1fe58e9d9c62369f81cdb65f851c7b18')
    }
    doc = None
    rdict = None
    while True:
        address = addr.encode("utf-8")
        p = urllib.parse.urlencode({'query': address})
        result = requests.get(f"http://{os.environ['CACHE_HOST']}:{os.environ['CACHE_PORT']}/v2/local/search/address.json", headers=headers, params=p)
        rdict = result.json()
        if 'documents' not in rdict:
            print('documents is not in the result:', rdict)
        doc = rdict['documents']
        # print(len(doc),addr, doc)
        if len(doc) == 0:
            addr = addr.rsplit(' ', 1)[0]
            # print(' retry>', end=' ')
            address = addr.encode("utf-8")
            continue
        break
    location = rdict['documents'][0]['address']
    # EPSG:5181 를  WGS84
    # x1,y1=float(location['x']),float(location['y'])
    x1, y1 = location['x'], location['y']
    # result=requests.get(f"https://localhost:50001/v2/local/geo/transcoord.json?x={x1}&y={y1}&output_coord=WGS84", headers=headers)
    # rdict=result.json()
    # doc=rdict['documents'][0]
    # x2,y2=doc['x'],doc['y']
    return pd.Series({'addr': addr, 'location': [float(y1), float(x1)]})
    # return row['name'], addr, (float(y2), float(x2))


class Place(BaseModel):
    key: str
    대표순서: str
    대표주소: str
    location: List[float]
    배달건: int


def label2json(labels, locations):
    clusters = {l: [] for l in range(len(set(labels)))}
    for i, l in enumerate(labels):
        clusters[l] += [locations[i]]
    return clusters


def solve_vrp(n_trucks, min_trucks, truck_capa, truck_tw, loc_demand, loc_tw, svc_time, location_names,
              cost_matrix, time_matrix, time_variance=10, n_loc_variance=2, think_time=1, ):
    """
    각 차량별 근무시간, 각 차량별 배달 가능량(용량), 배달지별 배달수량, 배달지별 도착해야하는 시간, 각 차량별 총 운행시간의 편차, 각 차량별 배달지 갯수의 편차를 해결 조건으로 전달하여 올바른 해를 찾는다.

    :param int n_trucks: 운행해야하는 차량의 총 대수 - 기본값:3대
    :param int truck_capa: 각 차량이 배송해야하는 물건의 갯수로 만일 각 차량별 차이를 두려면 이 갯수로 조정한다. - 기본값:[0,25]*n_trucks
    :param int truck_tw: 각 차량의 운행 시간에 대한 조건으로 [0,7*60] 을 기본값으로 하나 특정 차량이 일찍 끝나야할 때는 이 값을 이용한다.- 기본값:[0,420]*n_trucks
    :param int loc_demand: 각 배송지에 배달해야하는 물건의 수의 list. 만약, 한 주소지에 여러 물건 배송이 있다면 해당 방문지의 위치에는 1보다 큰 값을 부여한다. 기본값은 모든 항목이 1인 list
    :param int loc_tw: 배송지에 도착해야하는 시간대를 설정한 2D list로 각 배송지마다 [최소, 최대] 값을 부여한다. 기본값은 truck_tw의 기본값을 사용하며 [0,7*60] 하루 7시간 배송시간을 감안하여 이에 해당하는 420분을 설정. 만일, 특정 고객이 특정 시간대를 원할 경우 이 값을 이용하여 고객이 원하는 시간대를 상대값으로 설정한다. 본사 출발시각은 11시30분을 기준으로 함. - 기본값:[0,420]*n_trucks
    :param int svc_tm: 배송지에 도착후부터 배달후 다시 출발할 때까지의 소요시간 - 기본값:12
    :param list cost_matrix: 2D list 로 맵(내비)서비스에서 받은 자료에 기반하여 모든 노드간의 이동 거리를 측정한 데이터
    :param list time_matrix: 2D list 로 맵(내비)서비스에서 받은 자료에 기반하여 모든 노드간의 이동 시간을 측정한 데이터
    :param int time_variance: 분으로 맞춤 - 기본값:20분
    :param int n_loc_variance: 방문지 갯수 - 기본값:2곳
    :param int think_time: 문제 해결에 사용할 최대 시간 (초) - 기본값:1초
    :return dict: solution_cost:전체 차량을 운행할 때 측정되는 cost (총 거리의 합으로 예상됨), task_id:방문지의 index, arrival_stamp:본사 출발하여 경로를 순서대로 따라가 각 방문지 도착 까지 거리는 시간, route:해당 차량의 방문해야하는 방문지 index를 순서대로 담은 list 이며 차량의 ID는 A~Z
    """
    ip = "localhost"
    port = "5000"
    url = "http://" + ip + ":" + port + "/cuopt/"

    # initialize variables
    n_vehicles = n_trucks
    # n_vehicles = n_trucks + 2 if n_trucks > 0 else n_trucks
    # location_ids = [1 for i in range(len(location_names))]
    location_ids = [i + 1 for i in range(len(location_names) - 1)]  # exclude the fulfillment center from task data
    location_demand = [1] * len(location_ids) if loc_demand is None else loc_demand
    vehicle_capacity = [round(len(location_ids) / n_vehicles)] * n_vehicles if truck_capa is None else truck_capa
    vehicle_locs = [[0, 0]] * n_vehicles  # 본사에서 출발하여 본사로 돌아와야 하므로 기본 세팅해줌
    # n_locations = len(location_demand)
    # print( len(location_ids), vehicle_capacity, vehicle_locs)

    data_params = {"return_data_state": False}

    # Set the cost matrix and time matrix
    cost_data = {"cost_matrix": {0: cost_matrix}}
    response_set = requests.post(
        url + "set_cost_matrix", params=data_params, json=cost_data
    )
    assert response_set.status_code == 200

    # Set the time matrix
    dura_data = {"cost_matrix": {0: time_matrix}}
    response_set = requests.post(
        url + "set_travel_time_matrix", params=data_params, json=dura_data
    )
    assert response_set.status_code == 200

    # set capacity and deliveries data: task data + vehicle data
    task_data = {
        "task_locations": location_ids,
        "demand": [location_demand],
        "service_times": [12 if svc_time is None else svc_time] * len(location_demand)
    }
    ic(task_data)
    response_set = requests.post(url + "set_task_data", json=task_data)
    assert response_set.status_code == 200

    # veh_earliest = [  0]*n_vehicles # earliest a vehicle/tech start
    # veh_latest   = [380]*n_vehicles # end of the vehicle/tech shift
    # @rule: 각 차량별 근무시간을 제약조건으로 줌
    twindows = [[0, 100]] * n_vehicles
    print('vehicle_capacity', vehicle_capacity, )
    print('vehicle_locs', vehicle_locs)
    print('vehicle_time_windows', twindows)
    print('n_vehicles', n_vehicles)

    # @rule: 튜닝 데이터 정리 1
    fleet_data = {
        "vehicle_ids": [chr(ord('A') + i) for i in range(n_vehicles)],
        "vehicle_locations": vehicle_locs,
        "capacities": [vehicle_capacity],
        "min_vehicles": min_trucks,
        "drop_return_trips": [False] * n_vehicles,
        "skip_first_trips": [False] * n_vehicles,
        "vehicle_time_windows": truck_tw,
        "vehicle_max_time": [600] * n_vehicles,
    }
    response_set = requests.post(url + "set_fleet_data", json=fleet_data)
    ic(fleet_data, response_set.text)
    assert response_set.status_code == 200

    # solver settings
    # @rule: 튜닝 데이터 정리 2
    # objs= {
    #     "vehicle" :  0,
    #     "cost": 1,
    #     "variance_route_size": 26000, #골고루 분산하는 효과는 좋음
    #     "variance_route_service_time": 50 ,
    # }
    objs = {
        "vehicle": 0,
        "cost": 1,
        "variance_route_size": 3000,  # 골고루 분산하는 효과는 좋음
        "variance_route_service_time": 3500,
    }

    solver_config = {
        "time_limit": think_time,
        "number_of_climbers": 2048,
        "objectives": objs,
        "verbose_mode": True,
        "error_logging": True,
    }
    response_set = requests.post(url + "set_solver_config", json=solver_config)
    assert response_set.status_code == 200

    # @v Solve the problem
    solver_response = requests.get(url + "get_optimized_routes")
    print(solver_response.status_code, solver_response.text)
    assert solver_response.status_code == 200

    # Process returned data
    solver_resp = solver_response.json()["response"]["solver_response"]
    if solver_resp["status"] == 0:
        print("Cost for the routing in distance: ", solver_resp["solution_cost"])
        print("Vehicle count to complete routing: ", solver_resp["num_vehicles"])
        util_show_vehicle_routes(solver_resp, location_names)
    else:
        print("NVIDIA cuOpt Failed to find a solution with status : ", solver_resp["status"])

    # summary
    sum_df = None
    best_routes = {}
    for k in solver_resp['vehicle_data'].keys():
        print('k', k)
        selected_dict = {key: value for key, value in solver_resp['vehicle_data'][k].items() if key in ['task_id', 'arrival_stamp']}
        tmp = pd.DataFrame.from_dict(selected_dict)
        tmp['truck_id'] = k
        sum_df = tmp if sum_df is None else sum_df.append(tmp, ignore_index=True)
        best_routes[ord(k) - ord('A') + 1] = solver_resp['vehicle_data'][k]['route']
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    print(sum_df[['arrival_stamp', 'truck_id']].groupby('truck_id').max())
    return best_routes


# Prints vehicle routes
def util_show_vehicle_routes(resp, locations):
    solution = resp["vehicle_data"]
    for id in list(solution.keys()):
        route = solution[id]["route"]
        print("For vehicle -", id, "route is: \n")
        path = ""
        for index, route_id in enumerate(route):
            path += locations[route_id]
            if index != (len(route) - 1):
                path += "->"
        print(path + "\n\n")

#
# 2.15.10  2대는 풀캐파로, 한 대는 15개 캐파로 또 다른 한대는 10개 배송 캐파로 총 4대가 배송대상이 됨!
#


def parseCarDistStr(dotStr):
    print('############################')
    ic(dotStr)
    if '.' in dotStr:
        numArr = dotStr.split('.')
        ic(numArr)
        if numArr[0] == '':
            return 0, None
        ntruck = int(numArr[0]) + len(numArr) - 1
        lastCarsCapas = [int(n) for n in numArr if n.strip() != '' or int(n) > 0]  # "1.."
    else:
        ntruck = int(dotStr)
        lastCarsCapas = None
    print('############################')

    return ntruck, lastCarsCapas


def genTruckCapas(ntruck, vnum, lastCarsCapas, maxCapa):
    capas = None
    if lastCarsCapas is None:
        capas = [maxCapa if vnum > 0 else 100] * ntruck
    else:
        # ntruck+=len(lastCarsCapas)
        capas = [maxCapa if vnum > 0 else 100] * (ntruck - (len(lastCarsCapas) - 1))
        capas.extend(lastCarsCapas[1:])
        # for capa in lastCarsCapas:
        #     capas.append(capa)
    return ntruck, capas


@app.post("/clusters/{vnum_str}")
async def get_cluster_info(vnum_str: str, places: List[Place]):
    """배달 차량수에 따르는 배송지 그룹핑 및 방문 순서

    Returns:
        json: 배달차량 기호, 방문 순서서
    """
    vnum, lastCapas = parseCarDistStr(vnum_str)
    depot = {
        'key': '본사', '대표순서': '0', 'location': (37.5458880294551, 127.193631652802), '대표주소': '경기 하남시 하남대로 947'
    }
    shipments = [place.dict() for place in places]
    shipments_w_depot = [depot] + shipments
    locations = [[x['location'][1], x['location'][0]] for x in shipments_w_depot]
    location_names = [str(i) for i, vv in enumerate(locations)]
    # location_coordinates = [ [c[0],c[1]] for c in locations]
    # location_coordinates_df = pd.DataFrame(location_coordinates, columns=['xcord', 'ycord'], index=location_names)
    shipment_locations = [[37.5458880294551, 127.193631652802]] + [s['location'] for s in shipments]
    # shipment_locations2 = [[x[1], x[0]] for x in shipment_locations]

    print('shipments-----\n', shipments)
    # coords =  [ (x[0],x[1]) for x in shipment_locations]
    # print('coords-----\n',coords)

    # ref: https://openrouteservice.org/
    body = {"locations": locations, "metrics": ["distance", "duration"]}
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf6248b43b5f4e512e4bf99bb9ed55bd5f6a1f',
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post(f"http://{os.environ['ORS_HOST']}:{os.environ['ORS_PORT']}/ors/v2/matrix/driving-car", json=body, headers=headers)
    # call = requests.post('https://api.openrouteservice.org/v2/matrix/driving-car', json=body, headers=headers)

    # print(call.status_code, call.reason)
    print(call.text)
    dm_json = json.loads(call.text)['distances']
    print('distance_matrix ----------- \n', dm_json)

    # distance matrix
    distance_matrix = json.loads(call.text)['distances']
    cost_matrix = [[c for c in row] for row in distance_matrix]  # meter to km (c/1000)

    duration_matrix = json.loads(call.text)['durations']
    time_matrix = [[c / 60 for c in row] for row in duration_matrix]  # 각 장소마다 배송에 쓰는 시간 및 교통 상황 감안하여 여유율을 반영
    # time_matrix = [[(c / 50000) * 60 for c in row] for row in distance_matrix]  # 분으로 맞춤. 시간으로 하려면 (c/50000)  # 각 장소마다 배송에 쓰는 시간 및 교통 상황 감안하여 여유율을 반영
    # cmdf = pd.DataFrame(cost_matrix).astype('float')
    # print('cmdf=>', cmdf)
    # tmdf = pd.DataFrame(time_matrix).astype('float')
    # print('tmdf=>', tmdf)

    time_windows = {i + 1: (0, 7) for i in range(len(cost_matrix))}
    time_windows['Source'] = (0, 7)
    time_windows['Sink'] = (0, 7)
    # print('cost_matrix=>',cost_matrix)
    # print('time_windows', time_windows)

    # TODO 추후 복잡한 로직 처리 필요할 경우 이 파라메터를 UI에서 받아야 함.
    CAPA_MAX = 35  # 22가 최대치 이지만 추가 배송할 수도 있으며, 22개 넘는 배송지를 사전에 확인하는 용도로도 사용하므로 이 정도를 설정함
    # @rule: 튜닝 데이터 정리 3
    n_trucks = vnum if vnum > 0 else abs_one(vnum)
    truck_capa = [CAPA_MAX if vnum > 0 else 100] * n_trucks
    n_trucks, truck_capa = genTruckCapas(n_trucks, vnum, lastCapas, CAPA_MAX)
    min_trucks = abs_one(vnum)
    ic(n_trucks, min_trucks, truck_capa)

    locations_demand = [p.배달건 for p in places]
    truck_tw = [[0, 600]] * n_trucks  # if vnum> 0 else [0,360*2]]*n_trucks # 420 not working properly
    time_windows = [[0, 600]] * n_trucks  # if vnum> 0 else [0,360*2]]*len(locations_demand)
    service_time = 15
    loca_var = 1
    time_var = 1
    think_time = 10 if vnum > 0 else 0.01
    """
    cuOpt를 이용한 VRP 해 찾기
    """
    best_routes = solve_vrp(
        n_trucks,
        min_trucks,
        truck_capa,
        truck_tw,
        locations_demand,
        time_windows,
        service_time,
        location_names,
        cost_matrix,
        time_matrix,
        time_var,
        loca_var,
        think_time)
    # best_routes= solve_vrp(n_trucks, truck_capa, truck_tw, loc_demand, loc_tw, svc_time,locations, cost_matrix,time_matrix, time_variance=20, n_loc_variance=2, think_time=1, ):

    print('best_routes:', best_routes)
    # shipments 는 고객들의 좌표(location),name,주소 리스트
    # shipment_locations는 출발지인 본사의 위치를 포함한 좌표 리스트
    ret_info_json = {'routeinfo': {}, 'summary': []}
    cn = ord('A')
    thcks = [18, 16, 14, 12, 10, 8, 6, 4, 2]
    colors = ['#ffa8af', '#b794fc', '#4aeada', '#ffaffc', '#34eb8e', '#3659f4', '#9fbb8a', '#373886', '#11f1f1', '#cc9900']
    # colors=[' '#ff5348',#8530f8', '#0eaecc', '#ef6fe9','#15a84b' ,'#0304d0', '#6e7816', '#130553', '#4fcfef','#ff9905']
# imgsrc= ['mrk-red.png','mrk-violet.png','mrk-blue.png', 'mrk-pink.png','mrk-green.png','mrk-onlyblue.png','mrk-kaki.png','mrk-darkviolet.png','mrk-orange.png']
    n_routes = len(best_routes)
    ic(n_routes)
    for i, r in enumerate(list(best_routes.values())):
        dchar = chr(cn + i) if vnum > 0 else shipments[0]['대표순서']
        one_route_info = {}
        poly_coords = []
        distance = 0
        duration = 0
        sched_shipments = []
        deliver_num = 0
        # if i != 1:
        #     continue
        for j, l in enumerate(r):
            shpmts_locs = {}
            if j + 1 == len(r):
                break
            l_dest = 0 if r[j + 1] in ['Source', 'Sink'] else r[j + 1]
            l = 0 if l in ['Source', 'Sink'] else l
            orig_point = (shipment_locations[l][1], shipment_locations[l][0])
            dest_point = (shipment_locations[l_dest][1], shipment_locations[l_dest][0])
            coords = [orig_point, dest_point]
            # print('coords',coords)
            # coords = ((127.1449200822, 37.49588151 ),(127.1196367797,37.4801299358))
            g = i if vnum > 0 else ord(dchar) - ord('A')
            rc = colors[g]
            ic(g + (len(thcks) - n_routes))
            thck_index = g + (len(thcks) - n_routes) if vnum > 0 else len(thcks) + vnum
            thck = thcks[thck_index]

            client = openrouteservice.Client(base_url=f"http://{os.environ['ORS_HOST']}:{os.environ['ORS_PORT']}/ors",
                                             key='5b3ce3597851110001cf6248b43b5f4e512e4bf99bb9ed55bd5f6a1f')  # Specify your personal API key
            routes = client.directions(coords)
            geometry = routes['routes'][0]['geometry']
            poly_coords += polyline.decode(geometry)
            route_sum = routes['routes'][0]['summary']
            if route_sum == {}:
                distance += 0
                duration += 0
            else:
                dist = route_sum['distance']
                distance += dist
                # dura=route_sum['duration'] if 'duration' in route_sum.keys() else 0
                dura = dist / 50000 * 3600
                duration += dura  # 한 장소마다 10분씩 배달에 사용한다고 가정
                kmph = (dist / 1000) / (dura / 3600)
                # print(f'시속:{kmph}km/h', 'dura, dist', dura,dist)
                # duration*=1.2 # OepnStreetMap 이 duration에 여유율 1.2 를 반영
            if l == 0:
                if j > 0:
                    break
                if j == 0:
                    continue
            shpmts_locs['배달건'] = shipments[l - 1]['배달건']
            deliver_num += shpmts_locs['배달건']
            shpmts_locs['key'] = shipments[l - 1]['key'] if l > 0 or l < len(r) - 1 else '본사'
            shpmts_locs['location'] = shipments[l - 1]['location'] if l > 0 or l < len(r) - 1 else depot['location']
            shpmts_locs['대표주소'] = shipments[l - 1]['대표주소'] if j > 0 or j < len(r) - 1 else depot['대표주소']
            shpmts_locs['대표순서'] = f"{dchar}-{j:0>2}"
            shpmts_locs['icon'] = f"markers/mrk-d{ord(dchar)-ord('A')}-{j:0>2}.png"
            # print('icon-str',shpmts_locs['icon'], ',순서',shpmts_locs['대표순서'])
            sched_shipments.append(shpmts_locs)
            ret_info_json['routeinfo'][dchar] = {
                'deliver': shpmts_locs['배달건'],
                'distance': distance,
                'duration': duration,
                'routing': sched_shipments,
                'polyline': {
                    'color': rc,
                    'thickness': thck,
                    'coords': poly_coords}
            }
        ret_info_json['routeinfo'][dchar]['deliver'] = deliver_num

    ic(ret_info_json['routeinfo'].keys())

    for k in ret_info_json['routeinfo'].keys():
        all_visits = len(ret_info_json['routeinfo'][k]['routing'])
        all_dist = ret_info_json['routeinfo'][k]['distance'] / 1000
        drive_dura = ret_info_json['routeinfo'][k]['duration'] / 3600
        all_dura = drive_dura + (all_visits * 10) / 60  # 방문지마다 10분을 사용한다고 가정
        hm = str(datetime.timedelta(hours=all_dura))[:-7]
        h, m = int(all_dura), int((all_dura - int(all_dura)) * 60)
        deliver_num = ret_info_json['routeinfo'][k]['deliver']
        print(f'차량 {k} ==> 거리:{all_dist:3.2f} km, 소요시간: {h}시간{m}분, 평균시속: {all_dist/drive_dura:3.2f} km/h, 방문:{all_visits}곳')
        ret_info_json['summary'].append({'course': k,
                                         'distance': f'{all_dist:3.2f}',
                                         'all_dura': all_dura,
                                         'duration': f'{hm}',
                                         'durastr': f'{h}시간{m}분',
                                         'avgspeed': f'{all_dist/drive_dura:3.1f}',
                                         'visit': f'{all_visits}',
                                         'deliver': deliver_num})

    if vnum > 0:
        attach_summary(ret_info_json, '자동배차')
    return ret_info_json


@app.post("/routes")
async def merge_one_vrp_info(places: List[Place]):
    # ic(places)
    dchars = sorted(set(item.대표순서 for item in places))
    ic(dchars)
    ret_route_json = {'summary': [], 'routeinfo': {}}
    for dchar in dchars:
        one_course = [item for item in places if item.대표순서[0] is dchar]
        ic(one_course, dchar)
        # 차량 1개의 추천이지만 총 차량 갯수를 알수 있도록  음수로 전체 차량 수를 보낸다. 경로 탐색때는 1개 차량별로 받아내지만 경로인 폴리라인의 굵기나 색상 선택시에 필요하다.
        ret_info_json = await get_cluster_info(str(-1 * len(dchars)), one_course)
        # ic(ret_info_json)
        ret_route_json['summary'].append(ret_info_json['summary'][0])
        # ret_route_json['summary'][-1]['course'] = dchar
        ret_route_json['routeinfo'][dchar] = ret_info_json['routeinfo'][dchar]
    attach_summary(ret_route_json, '수동배차')
    return ret_route_json


def attach_summary(info_dict, schedulType):
    print('----------------------------')
    ic(info_dict['summary'])
    print('----------------------------')
    dt = datetime.datetime.now().strftime('%Y-%m-%d')
    sum_rinfo = {"course": "요약", "distance": 0, "duration": 0, "avgspeed": 0, "visit": 0, "deliver": 0, "count": 0, "method": schedulType, "date": dt}
    all_dura = 0
    max_dura = 0
    min_dura = 10000
    for item in info_dict['summary']:
        item['method'] = schedulType
        item['date'] = dt
        sum_rinfo["distance"] += float(item["distance"])
        # sum_rinfo["duration"] += int(item["duration"])
        sum_rinfo["avgspeed"] += float(item["avgspeed"])
        sum_rinfo["visit"] += int(item["visit"])
        sum_rinfo["deliver"] += int(item["deliver"])
        sum_rinfo["count"] += 1
        if max_dura < item["all_dura"]:
            max_dura = item["all_dura"]
        if min_dura > item["all_dura"]:
            min_dura = item["all_dura"]
        all_dura += item["all_dura"]

    for item in info_dict['summary']:
        dff = max_dura - item["all_dura"]
        item['durastr'] = str(datetime.timedelta(hours=dff))[:-7]

    total_duration = str(datetime.timedelta(hours=all_dura))[:-7]
    dura_minmax_diff = str(datetime.timedelta(hours=max_dura - min_dura))[:-7]
    # h, m = int(all_dura), int((all_dura - int(all_dura)) * 60)
    # total_durastr = f'{h}시간{m}분'
    sum_rinfo["avgspeed"] = f'{sum_rinfo["avgspeed"] / sum_rinfo["count"]:3.1f}'
    sum_rinfo["durastr"] = dura_minmax_diff
    sum_rinfo["duration"] = total_duration
    sum_rinfo["course"] = '요약'
    info_dict['summary'].append(sum_rinfo)
    info_dict['summary'] = [{k: v for k, v in d.items() if k not in ['all_dura']} for d in info_dict['summary']]
    ic(info_dict['summary'])
    return info_dict
