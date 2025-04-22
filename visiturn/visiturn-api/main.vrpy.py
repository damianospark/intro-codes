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

# import faster_than_requests as requests
# import re
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


@app.post("/clusters/{vnum}")
async def get_cluster_info(vnum: int, places: List[Place]):
    """배달 차량수에 따르는 배송지 그룹핑 및 방문 순서

    Returns:
        json: 배달차량 기호, 방문 순서서
    """

    depot = {
        'key': '본사', '대표순서': '0', 'location': (37.5458880294551, 127.193631652802), '대표주소': '경기 하남시 하남대로 947'
    }
    records = [place.dict() for place in places]
    ic(records)
    shipments = records
    shipment_locations = [[37.5458880294551, 127.193631652802]] + [s['location'] for s in shipments]
    shipment_locations2 = [[x[1], x[0]] for x in shipment_locations]

    print('shipments-----\n', shipments)
    # print('shipment_locations-----\n', shipment_locations)
    # print('shipment_locations2-----\n',shipment_locations2)
    # coords =  [ (x[0],x[1]) for x in shipment_locations]
    # print('coords-----\n',coords)

    # ref: https://openrouteservice.org/
    body = {"locations": shipment_locations2, "metrics": ["distance", "duration"]}
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
    cmdf = pd.DataFrame(cost_matrix).astype('float')
    print('cmdf=>', cmdf)
    tmdf = pd.DataFrame(time_matrix).astype('float')
    print('tmdf=>', tmdf)

    time_windows = {i + 1: (0, 7) for i in range(len(cost_matrix))}
    time_windows['Source'] = (0, 7)
    time_windows['Sink'] = (0, 7)
    # print('cost_matrix=>',cost_matrix)
    # print('time_windows', time_windows)
    # 거리 기반의 cost 그래프 생성
    diG = DiGraph()
    for i, row in enumerate(cost_matrix):
        for j, cell in enumerate(row):
            if i == 0 and j == 0:
                continue
            diG.add_edge("Source" if i == 0 else i, "Sink" if j == 0 else j, cost=cell)
    # print('diG.nodes=>', diG.nodes)

    # 시간 제약을 위해 각 엣지에 소요 시간 마킹
    for (u, v) in diG.edges():
        u2 = 0 if u == 'Source' else u
        v2 = 0 if v == 'Sink' else v
        diG.edges[u, v]["time"] = time_matrix[u2][v2]
        # print('time',u,v,time_matrix[u2][v2])
    # @rule : don't delete
    # # start setting time_windows
    # for v in diG.nodes():
    #     diG.nodes[v]["lower"] = time_windows[v][0]
    #     diG.nodes[v]["upper"] = time_windows[v][1]
    #     if v not in ["Source", "Sink"]:
    #         diG.nodes[v]["service_time"] = 0.16  # 기사가 각 노드에서 배달에 보내는 시간 0.08시간=약 5분 TODO: 파라메터로 추출 필요
    # end setting time_windows
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    prob = VehicleRoutingProblem(diG, num_vehicles=abs_one(vnum), minimize_global_span=False, time_windows=False, duration=int(12 * 60))

    # prob.fixed_cost = 100
    # prob.use_all_vehicles = True
    # prob._greedy=False
    prob.num_stops = int(len(cost_matrix) / abs_one(vnum) + 1)
    prob.solve(time_limit=3, max_iter=5, pricing_strategy="Exact")  # TODO: change 60 to 180??? ,Exact, BestEdges1, BestEdges2, BestPaths
    # prob.solve(time_limit=300,cspy=False, solver='cplex') #TODO: change 60 to 180??? ,Exact, BestEdges1, BestEdges2, BestPaths
    print('best_routes:', prob.best_routes)
    # shipments 는 고객들의 좌표(location),name,주소 리스트
    # shipment_locations는 출발지인 본사의 위치를 포함한 좌표 리스트
    ret_info_json = {'routeinfo': {}, 'summary': []}
    cn = ord('A')
    thcks = [18, 16, 14, 12, 10, 8, 6, 4, 2]
    colors = ['#ffa8af', '#b794fc', '#4aeada', '#ffaffc', '#34eb8e', '#3659f4', '#9fbb8a', '#373886', '#11f1f1', '#cc9900']
    # colors=[' '#ff5348',#8530f8', '#0eaecc', '#ef6fe9','#15a84b' ,'#0304d0', '#6e7816', '#130553', '#4fcfef','#ff9905']
# imgsrc= ['mrk-red.png','mrk-violet.png','mrk-blue.png', 'mrk-pink.png','mrk-green.png','mrk-onlyblue.png','mrk-kaki.png','mrk-darkviolet.png','mrk-orange.png']

    for i, r in enumerate(list(prob.best_routes.values())):
        dchar = chr(cn + i) if vnum > 0 else records[0]['대표순서']
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
            g = i if vnum >= 0 else ord(dchar) - ord('A')
            rc = colors[g]
            thck = thcks[g + (len(thcks) - abs(vnum))]

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
        ret_info_json = await get_cluster_info(-1 * len(dchars), one_course)  # 차량 1개의 추천이지만 총 차량 갯수를 알수 있도록  음수로 전체 차량 수를 보낸다. 경로 탐색때는 1개 차량별로 받아내지만 경로인 폴리라인의 굵기나 색상 선택시에 필요하다.
        # ic(ret_info_json)
        ret_route_json['summary'].append(ret_info_json['summary'][0])
        # ret_route_json['summary'][-1]['course'] = dchar
        ret_route_json['routeinfo'][dchar] = ret_info_json['routeinfo'][dchar]
    attach_summary(ret_route_json,'수동배차')
    return ret_route_json


def attach_summary(info_dict, schedulType):
    print('----------------------------')
    ic(info_dict['summary'])
    print('----------------------------')
    dt=datetime.datetime.now().strftime('%Y-%m-%d')
    sum_rinfo = {"course": "요약", "distance": 0, "duration": 0, "avgspeed": 0, "visit": 0, "deliver": 0, "count": 0, "method":schedulType, "date": dt }
    all_dura = 0
    for item in info_dict['summary']:
        item['method']=schedulType
        item['date']=dt
        sum_rinfo["distance"] += float(item["distance"])
        # sum_rinfo["duration"] += int(item["duration"])
        sum_rinfo["avgspeed"] += float(item["avgspeed"])
        sum_rinfo["visit"] += int(item["visit"])
        sum_rinfo["deliver"] += int(item["deliver"])
        sum_rinfo["count"] += 1
        all_dura += item["all_dura"]
    total_duration = str(datetime.timedelta(hours=all_dura))[:-7]
    h, m = int(all_dura), int((all_dura - int(all_dura)) * 60)
    total_durastr = f'{h}시간{m}분'
    sum_rinfo["avgspeed"] = f'{sum_rinfo["avgspeed"] / sum_rinfo["count"]:3.1f}'
    sum_rinfo["durastr"] = total_durastr
    sum_rinfo["duration"] = total_duration
    sum_rinfo["course"] = '요약'
    info_dict['summary'].append(sum_rinfo)
    info_dict['summary'] = [{k: v for k, v in d.items() if k not in ['all_dura']} for d in info_dict['summary']]
    ic(info_dict['summary'])
    return info_dict
