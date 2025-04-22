import React, { useEffect, useMemo, useState } from "react";
// import * as geolib from "geolib";
import * as turf from "@turf/turf";
import * as dfd from "danfojs";
import axios from "axios";
import * as amplitude from "@amplitude/analytics-browser";
import _ from "lodash";

// papaParse : https://joshtronic.com/2022/05/15/how-to-convert-csv-to-json-in-javascript/
// multiline str : https://stackoverflow.com/questions/805107/creating-multiline-strings-in-javascript
// danfo dataframe : https://blog.tensorflow.org/2020/08/introducing-danfo-js-pandas-like-library-in-javascript.html
// geolib : https://github.com/manuelbieh/geolib [x]
// Turf.js : https://turfjs.org/docs/#center [O] yarn add @turf/turf
// https://codesandbox.io/s/mueyi?file=/src/index.js

// Error: ENOSPC: System limit for number of file watchers reached
// Solution: echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

// import { Map } from "typescript";
// import * as Papa from 'papaparse'

// ref: Todo Tree의 guter icon 설정시 찾아볼 icon libraries, 해당 플러그인이 이 패키지를 사용하고 있음.
// https://microsoft.github.io/vscode-codicons/dist/codicon.html

// import https from "https";
// const https = require("https");
// const https = require("https-browserify");

amplitude.init("d6fbe28f1b2bb2f937ca80859d58424c");
//import specific methods/classes
// import { readCSV, DataFrame } from "danfojs";
// import fs from fs;
// const fs = require("fs");
const Papa = require("papaparse");
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
process.env.npm_config_strict_ssl = "false";

const { kakao } = window;
declare global {
    interface Window {
        kakao: any;
    }
    // interface OldValue {
    //     // @v NewValue : 이름주소전화 key 대표주소 대표순서 순서 모두 갖고 있는 자료구조
    //     key: string;
    //     location: [number, number];
    //     대표주소: string;
    //     대표순서: string;
    //     이름: string[];
    //     주소: string[];
    //     주소2: string[];
    //     순서: string[];
    //     전화: string[];
    // }
    interface NewValue {
        // @v NewValue : 이름주소전화 key 대표주소 대표순서 순서 모두 갖고 있는 자료구조
        icon: string;
        대표주소: string;
        대표순서: string;
        location: [number, number];
        이름: string[];
        주소: string[];
        주소2: string[];
        순서: string[];
        전화: string[];
        key: string;
        차량: string;
    }
    interface VrpValue {
        icon: string;
        key: string;
        대표순서: string;
        대표주소: string;
        location: [number, number];
        배달건: number;
    }
}

// let map: any;
let mlvl = 7;
const pts: any[] = [];
var lati = 37.5145636;
var longi = 127.1059186;
var center_changed = false;

const global_markers: any[] = [];
const global_overlays: any[] = [];
const global_badges: any[] = [];
const global_polylines: any[] = [];
const imageSize = new kakao.maps.Size(24, 35);

// @v addrList Join is needed
async function generateDispatchList4TextArea(oldValues: any[] | null, nvalues: NewValue[], setToTextArea: (arg0: any) => void) {
    const oneUserAddrs = nvalues.filter((nv) => nv.이름.length === 1);
    const multiUserAddrs = nvalues.filter((nv) => nv.이름.length > 1);
    const newOneUserAddrs: any = [];
    multiUserAddrs.forEach((nv: NewValue) => {
        for (let i = 0; i < nv.이름.length; i++) {
            newOneUserAddrs.push({
                대표주소: nv.대표주소,
                대표순서: nv.대표순서,
                location: nv.location,
                이름: nv.이름[i],
                주소: nv.주소[i],
                주소2: nv.주소2[i],
                순서: nv.순서[i],
                전화: nv.전화[i],
                key: nv.key,
            });
            console.log("newOneUserAddrs increasing?", newOneUserAddrs.length);
        }
    });
    var newMultiUserAddrs = oneUserAddrs.concat(newOneUserAddrs);
    newMultiUserAddrs = _.sortBy(newMultiUserAddrs, "순서");
    const updatedAddrs: NewValue[] = newMultiUserAddrs.map((el: NewValue) => {
        return {
            ...el,
            차량: el.대표순서.substring(0, 1),
        };
    });
    if (oldValues == null) {
        return "";
    }
    console.log("updatedAddrs : ", updatedAddrs);
    console.log("oldValues : ", oldValues);

    const mergedArray: { [key: string]: any }[] = updatedAddrs.map((addr) => {
        const { 순서, ...details } = oldValues.find((oldValue) => oldValue["고객 KEY"].includes(addr.이름)) || {};
        console.log("addr : ", addr);
        console.log("oldValues : ", oldValues);
        return { 차량: addr.차량, 순서: addr.대표순서, ...details };
    });

    var csv = Papa.unparse(mergedArray, {
        // columns: ["차량", "순서", "이름", "주소", "전화", "주소2", "대표주소", "대표순서", "key", "location"],
        delimiter: "\t",
    });
    // console.log("csv==>", csv);
    setToTextArea(csv);
}

function isLocationsClustered(rawAddrList: NewValue[]) {
    const alphas = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i));
    return rawAddrList.every((item) => typeof item["대표순서"] === "string" && alphas.includes(item["대표순서"]));
}

function addMarkers(rawAddrList: NewValue[], isCourseMarked: boolean) {
    // console.log("rawAddrList", JSON.stringify(rawAddrList));
    console.log("rawAddrList", rawAddrList);
    global_markers.splice(0, global_markers.length);
    global_badges.splice(0, global_badges.length);
    rawAddrList?.forEach((el: NewValue) => {
        if (typeof el.순서[0] == "undefined" || el.순서[0] == null || el.순서[0] === "") el.순서[0] = "0";
        if (typeof el.전화[0] == "undefined" || el.전화[0] == null || el.전화[0] === "") el.전화[0] = "없음";
        // const imageSize = new kakao.maps.Size(24, 35);
        const imgPath = el.icon && el.icon.length > 5 ? el.icon : `./markers/dmrk-${el.대표순서.charAt(0)}.png`;
        var imageSrc = isCourseMarked ? imgPath : "./red-location.png";
        // console.log("imgPath", imgPath, "imageSrc", imageSrc);

        var markerImage = new kakao.maps.MarkerImage(imageSrc, imageSize);
        const markerPosition = new kakao.maps.LatLng(el.location[0], el.location[1]);
        const marker = new kakao.maps.Marker({
            map: kmap, // 마커를 표시할 지도
            position: markerPosition, // 마커를 표시할 위치
            title: el.대표주소, // 마커의 타이틀, 마커에 마우스를 올리면 타이틀이 표시됩니다
            image: markerImage, // 마커 이미지
            zIndex: 5,
        });
        // console.log(el.key, el.대표순서);
        global_markers.push({ key: el.key, mrk: marker });
        if (el.이름.length > 1) {
            let content = `<div><span class="notify-badge">${el.이름.length}</span></div>`;
            const frag = document.createRange().createContextualFragment(content);
            var badge = new kakao.maps.CustomOverlay({
                content: frag,
                map: kmap,
                position: markerPosition,
                zIndex: 7,
            });

            global_badges.push({
                // global_overlays.push({
                key: el.key,
                ovl: badge,
            });
        }
    });
    // issue : depotMarker를 global_markers에 추가하여 관리할 지 고민 필요
    const depotMarker = new kakao.maps.Marker({
        map: kmap, // 마커를 표시할 지도
        position: new kakao.maps.LatLng(37.5458880294551, 127.193631652802), // 마커를 표시할 위치
        title: "경기 하남시 하남대로 947", // 마커의 타이틀, 마커에 마우스를 올리면 타이틀이 표시됩니다
        image: new kakao.maps.MarkerImage("cb_dark.png", new kakao.maps.Size(50, 50)), // 마커 이미지
        zIndex: 5,
    });
}

function addInfoPanelOverlays(rawAddrList: NewValue[], isCourseMarked: boolean, showInfoPanel: boolean) {
    //todo: addMarders 에서 먼저 el 의 값을 변경한 것이 이 함수에 들어올 때도 반영되어 있는 지 확인
    if (global_markers.length === 0) return;
    global_overlays.splice(0, global_overlays.length);
    rawAddrList.forEach((el: NewValue) => {
        var subListdivs = "";
        for (var i = 0; i < el.주소.length; i++) {
            // const addrSub = el.주소[i].match(reAddrSplit);
            const addrSub = el.주소2[i];
            const seq = el.순서[i];
            const nm = el.이름[i];
            const tel = el.전화[i];
            subListdivs += `                <div class="ellipsis">${seq} / ${nm} / <b>${addrSub}</b> / ${tel} </div>`;
        }
        let content =
            '<div class="wrap">' +
            '    <div class="info">' +
            '        <div class="title">' +
            `            ${el.대표순서}. ${el.대표주소}` +
            `            <div class="close" title="닫기"  ></div>` +
            "        </div>" +
            '        <div class="body">' +
            '            <div class="desc">' +
            subListdivs +
            // '                <div><a href="https://www.kakaocorp.com/main" target="_blank" class="link">홈페이지</a></div>' +
            "            </div>" +
            "        </div>" +
            "    </div>" +
            "</div>";
        // https://davidwalsh.name/convert-html-stings-dom-nodes
        const frag = document.createRange().createContextualFragment(content);
        // console.log("frag", frag);
        // console.log("fcid", frag.firstChild);
        // console.log("fcid", frag.querySelector(".close"));
        const position = new kakao.maps.LatLng(el.location[0], el.location[1]);
        frag.querySelector(".close")?.addEventListener("click", function () {
            overlay.setMap(null);
        });
        var overlay = new kakao.maps.CustomOverlay({
            content: frag,
            map: kmap,
            position: position,
            zIndex: 7,
        });

        global_overlays.push({
            key: el.key,
            ovl: overlay,
        });

        // console.log("global_markers, ", global_markers);
        // console.log("el.key", el.key);
        const mrk_dict = global_markers.find((d) => d.key === el.key);
        if (!showInfoPanel) overlay.setMap();

        const marker = mrk_dict.mrk;
        kakao.maps.event.addListener(marker, "click", function () {
            amplitude.track("marker_clicked");
            overlay.setMap(!overlay.getMap() ? kmap : null);
        });
    });
}
async function drawRoutes(map: any, data: any) {
    const locAddrDict = new Map<string, any>();
    // const markers = new Map<string, any>();
    console.log("data from fastapi-----------------\n", data);
    global_overlays.forEach(function (ovl_dict) {
        ovl_dict.ovl.setMap(null);
    });
    let keys = Object.keys(data);
    // const imageSize = new kakao.maps.Size(24, 35);
    for (let k of keys) {
        const coords: any[] = [];
        const line_color = data[k]["polyline"]["color"];
        const line_tick = data[k]["polyline"]["thickness"];
        data[k]["routing"].forEach((r: any) => {
            locAddrDict.set(r["key"], r);
        });
        data[k]["polyline"]["coords"].forEach((loc: number[]) => {
            coords.push(new kakao.maps.LatLng(loc[0], loc[1]));
        });
        // console.log(coords);

        const polyline = new kakao.maps.Polyline({
            path: coords,
            strokeWeight: line_tick,
            strokeColor: line_color,
            strokeOpacity: 1,
            zIndex: 3,
        });
        // @rule : zindex --> 경로(polyline): 3 , marker:5, overlay:7
        // polyline.setZIndex(3); //ref: https://apis.map.kakao.com/web/documentation/#Marker_setZIndex
        polyline.setMap(map);
        global_polylines.push(polyline);

        // data[k]["routing"].forEach((pos: { key: string; location: any[]; 대표주소: string; 대표순서: string; icon: string }) => {
        //     // ref: : https://devtalk.kakao.com/t/topic/103147/2?u=lea.ju
        //     if (global_markers.length === 0) {
        //         const marker = new kakao.maps.Marker({
        //             map: map, // 마커를 표시할 지도
        //             position: new kakao.maps.LatLng(pos.location[0], pos.location[1]), // 마커를 표시할 위치
        //             title: pos.대표주소, // 마커의 타이틀, 마커에 마우스를 올리면 타이틀이 표시됩니다
        //             image: new kakao.maps.MarkerImage(pos.icon, new kakao.maps.Size(24, 35)), // 마커 이미지
        //         });
        //         global_markers.push({ key: pos.key, mrk: marker });

        //         if (global_overlays.length === 0) {
        //         } else {
        //             kakao.maps.event.addListener(marker, "click", function () {
        //                 // amplitude.track("marker_clicked");
        //                 const ovl_dict = global_overlays.find((d) => d.key === pos.key);
        //                 const overlay = ovl_dict.ovl;
        //                 overlay.setMap(!overlay.getMap() ? map : null);
        //             });
        //         }
        //     }
        //     // global_markers.set(pos.key, marker);
        // });
    }
    return locAddrDict;
}

// const agent = new https.Agent({
//     rejectUnauthorized: false,
//     requestCert: false,
// });
async function getLatLngFromAddr(x: any, index: number) {
    const trm_addr = x["주소"].split("(")[0];

    try {
        const res = await axios.get(`https://${process.env.REACT_APP_CACHE_HOST}:${process.env.REACT_APP_CACHE_PORT}/v2/local/search/address.json`, {
            headers: {
                "Content-Type": "application/json; charset=utf-8",
                Authorization: "KakaoAK 1fe58e9d9c62369f81cdb65f851c7b18",
            },

            params: { query: trm_addr },

            // httpsAgent: agent,
        });
        const data = await res.data;
        var lat = 0;
        var lng = 0;
        var cpr = "N";
        var mdn = "없음";
        if (data["documents"].length === 0) {
            console.log("다음의 주소가 검색되지 않습니다==> ", x["주소"], trm_addr);
            alert(`다음의 주소가 검색되지 않습니다. 확인해주세요. \n\n 주소:${x["주소"]}\n 고객명:${x["이름"]}`);
            // console.log(data);
            lat = 0;
            lng = 0;
            cpr = "N";
        } else {
            const match_first = data["documents"][0]["address"];
            // @rule : 소수점 5째 자리까지 정도면 국내 지도 표현에 무리가 없는 것으로 판단하여 소수점 5째 자리까지로 반올림하여 맞춤
            lat = parseFloat(parseFloat(match_first["y"]).toFixed(5));
            lng = parseFloat(parseFloat(match_first["x"]).toFixed(5));
            cpr = "Y";
            mdn = x["전화"];
        }
        x["key"] = lat + "-" + lng;
        const reAddrSplit =
            /([0-9a-zA-Z가나다라마바사]+차.*[0-9a-zA-Z가나다라마바사]+동.*[a-zA-Z0-9]+호.*|[0-9a-zA-Z가나다라마바사]+동.*[a-zA-Z0-9]+호.*|[동서남북]관.*[0-9a-zA-Z]+호.*|[0-9a-zA-Z]+호.*|[0-9]+층.*|[0-9]+-[0-9]+[\r\n\t\f])/gi;
        const addrMain = x.주소.replace(reAddrSplit, "");
        // console.log("elm>>>", elm)
        const addrSub = x.주소.match(reAddrSplit);
        x["주소2"] = [];
        if (addrSub != null) {
            x["주소2"].push(addrSub[0]);
        }
        const order = x["순서"] == null || x["순서"] === "" ? "0" : x["순서"];
        x["순서"] = [order];
        x["대표순서"] = order;
        x["대표주소"] = addrMain;
        x["전화"] = [mdn];
        x["이름"] = [x["이름"]];
        x["주소"] = [x["주소"]];
        // x["순서"] = index + 1;
        // REFACT  x["location"] = [lat,lng] or 반대로
        // x["latitude"] = lat;
        // x["longitude"] = lng;
        x["location"] = [lat, lng];
        // x["can_proc"] = cpr;
        if (cpr === "Y") pts.push([lat, lng]);
    } catch (err) {
        console.log("Error >>", err);
    }
    return x;
}

var options = {
    //지도를 생성할 때 필요한 기본 옵션
    center: new kakao.maps.LatLng(lati, longi), //지도의 중심좌표.
    level: mlvl, //지도의 레벨(확대, 축소 정도)
};
var kmap: any = null; //지도 생성 및 객체 리턴    }, []);
const ret: NewValue[] = [];
const raw_values: NewValue[] = [];
const sumed_values: VrpValue[] = [];
type Props = {
    addrList: string;
    showPanel: boolean;
    numDrivers: string;
    disableVrpButton: (isRendered: boolean) => void;
    setToTextArea: (dcsv: string) => void;
    setToDrawer: (route_info: any) => void;
};
// kakao multi overlay : https://velog.io/@seokkitdo/React-kakao-map-api-%EC%97%AC%EB%9F%AC%EA%B0%9C-%EB%A7%88%EC%BB%A4%EC%99%80-%EC%BB%A4%EC%8A%A4%ED%85%80%EC%98%A4%EB%B2%84%EB%A0%88%EC%9D%B4
const MapContainer: React.FC<Props> = ({ addrList, showPanel, numDrivers, disableVrpButton, setToTextArea, setToDrawer }: Props) => {
    const [isRendered, setIsRendered] = useState(true);
    const [dcsv, setDcsv] = useState("");
    const [rawValues, setRawValues] = useState(raw_values);
    const [oldValues, setOldValues] = useState(null);
    const [sumedValues, setSumedValues] = useState(sumed_values);
    // var rawValues: NewValue[] = [];
    // var sumedValues: VrpValue[] = [];

    console.log("numDrivers>>>>", numDrivers);
    var center: any = null;

    function addInfoToSumDictArr(dictArr: NewValue[], vrpvalues: VrpValue[], elm: NewValue) {
        const k: string = "key";
        const v: string = elm.location[0] + "-" + elm.location[1];
        const delivery_item = dictArr.find((d) => d.key === v);
        const vrp_item = vrpvalues.find((d) => d.key === v);
        // var idx = whichHasKeyValue(k, v, dictArr);
        if (delivery_item) {
            // dictArr[idx]["대표순서"] = elm.순서[0];
            if (!delivery_item?.대표주소.includes(elm.대표주소)) {
                delivery_item.대표주소 = delivery_item?.대표주소 + "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + elm.대표주소;
            }
            delivery_item?.주소.push(elm.주소[0]);
            delivery_item?.주소2.push(elm.주소2[0]);
            delivery_item?.순서.push(elm.순서[0]);
            delivery_item?.이름.push(elm.이름[0]);
            delivery_item?.전화.push(elm.전화[0]);
        } else {
            dictArr.push({
                icon: elm.icon,
                key: v,
                대표주소: elm.대표주소,
                대표순서: elm.대표순서,
                주소: elm.주소,
                주소2: elm.주소2,
                전화: elm.전화,
                이름: elm.이름,
                순서: elm.순서,
                location: elm.location,
                차량: elm.차량,
            });
        }

        if (!vrp_item) {
            vrpvalues.push({
                icon: "",
                key: elm.key,
                대표순서: elm.대표순서,
                대표주소: elm.대표주소,
                location: elm.location,
                배달건: 1,
            });
        } else {
            vrp_item.배달건 += 1;
        }
    }

    function refineRawData(txtFromGsheet: string) {
        // var ret: any[] = [];

        const tfRe = /TRUE\t.*/gi;
        const addrfix1Re = / ([가-힣]+동)([0-9])/gi;
        const addrfix2Re = / ([가-힣]+로)([0-9])/gi;

        const orders = txtFromGsheet
            .replace("배송지 주소", "주소")
            .replace("주소 리스트", "주소")
            .replace("고객 KEY", "이름")
            .replace("휴대폰 번호", "전화")
            .replace(tfRe, "")
            .replace(addrfix1Re, " $1 $2")
            .replace(addrfix2Re, " $1 $2");

        const orgOrders = txtFromGsheet.replace(tfRe, "");

        const jsonData = Papa.parse(orders, {
            header: true,
            delimiter: "\t",
            skipEmptyLines: true,
        });
        const orgJsonData = Papa.parse(orgOrders, {
            header: true,
            delimiter: "\t",
            skipEmptyLines: true,
        });

        console.log("refineRawData:jsonData  ---->", orgJsonData.data);
        setOldValues(orgJsonData.data);

        // 주소로부터 latitude, longitude 얻기
        pts.splice(0, pts.length);
        Promise.all(
            jsonData.data.map(async (r: any, i: number) => {
                const val = await getLatLngFromAddr(r, i);
                return val;
            })
        ).then((newValues) => {
            console.log("ret in refineRawData: newValues=>", newValues);
            // setNewValues(results);
            // rawValues.splice(0, rawValues.length);
            // sumedValues.splice(0, sumedValues.length);
            const nvalues: NewValue[] = [];
            const vrp_values: VrpValue[] = [];
            for (let r of newValues) {
                addInfoToSumDictArr(nvalues, vrp_values, r);
            }
            setRawValues(nvalues);
            setSumedValues(vrp_values);
            // console.log("useMemo:rawValues---->", rawValues);
            // console.log("useMemo:sumedValues---->", sumedValues);
        });

        // return ret;
    }

    useEffect(() => {
        if (addrList && addrList.length) {
            refineRawData(addrList);
        } else {
            rawValues.splice(0, addrList.length);
            sumedValues.splice(0, addrList.length);
            global_markers.splice(0, global_markers.length);
            global_overlays.splice(0, global_overlays.length);
            global_badges.splice(0, global_badges.length);
            global_polylines.splice(0, global_polylines.length);
            numDrivers = "0";
            setToTextArea("");
        }
        if (numDrivers === "0") disableVrpButton(true);
    }, [addrList]);

    useEffect(() => {
        if (global_overlays && global_overlays.length) {
            global_overlays.forEach((overlay) => overlay.ovl.setMap(showPanel ? kmap : null));
        }
    }, [showPanel]);

    useEffect(() => {
        console.log("useEffect2:nvalues---->", rawValues);
        console.log("useEffect2:vrp_values---->", sumedValues);

        var container = document.getElementById("map"); //지도를 담을 영역의 DOM 레퍼런스
        kmap = new kakao.maps.Map(container, options);
        if (!addrList || !addrList.length) {
            return () => {
                global_overlays &&
                    global_overlays.length > 0 &&
                    global_overlays.forEach(function (el) {
                        el.ovl.setMap(null);
                    });
                global_markers?.forEach(function (el) {
                    el.mrk.setMap(null);
                });
            };
        }
        if (pts && pts.length && !center_changed) {
            // console.log("pts => ", pts);
            var fts = turf.points(pts);
            // console.log("pts", pts);
            // console.log("features==>", fts);
            center = turf.center(fts);
            // console.log("center==>", center);
            lati = center.geometry.coordinates[0];
            longi = center.geometry.coordinates[1];
        }
        // 일반 지도와 스카이뷰로 지도 타입을 전환할 수 있는 지도타입 컨트롤을 생성합니다
        const moveLatLon = new kakao.maps.LatLng(lati, longi);
        // 지도 중심을 이동 시킵니다
        kmap.panTo(moveLatLon);
        const mapTypeControl = new kakao.maps.MapTypeControl();
        // 지도에 컨트롤을 추가해야 지도위에 표시됩니다
        // kakao.maps.ControlPosition은 컨트롤이 표시될 위치를 정의하는데 TOPRIGHT는 오른쪽 위를 의미합니다
        kmap.addControl(mapTypeControl, kakao.maps.ControlPosition.TOPRIGHT);
        // 지도 확대 축소를 제어할 수 있는  줌 컨트롤을 생성합니다
        const zoomControl = new kakao.maps.ZoomControl();
        kmap.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

        if (!parseInt(numDrivers, 10)) {
            console.log("=====================================================");
            /*경로 추천이 아닌 수동 그룹핑한 결과 넘버링해보기*/
            const canGroupMarkers = isLocationsClustered(rawValues);
            if (canGroupMarkers && sumedValues.length) {
                console.log("############sumedValues", sumedValues, sumedValues.length);
                axios
                    .post(
                        `https://${process.env.REACT_APP_VRP_HOST}:${process.env.REACT_APP_VRP_PORT}/routes`,
                        sumedValues
                        // { httpsAgent: agent }
                    )
                    .then((res) => {
                        console.log("res.data", res.data);
                        drawRoutes(kmap, res.data["routeinfo"]);
                        setToDrawer(res.data["summary"]);
                        // onRenderingChange(true);
                    });
                // )
            }
            // @v  순서 정하기 전의 최초 데이터로 마커 와 오버레이 그리기
            // console.log("rawValues", rawValues);
            addMarkers(rawValues, canGroupMarkers);
            addInfoPanelOverlays(rawValues, canGroupMarkers, showPanel);
            disableVrpButton(false);
        }

        kakao.maps.event.addListener(kmap, "zoom_changed", function () {
            // 지도의 현재 레벨을 얻어옵니다
            var level = kmap.getLevel();
            mlvl = level;
            amplitude.track("zoom_changed:" + level);
            // var message = '현재 지도 레벨은 ' + level + ' 입니다';
            // var resultDiv = document.getElementById('result');
            // resultDiv.innerHTML = message;
        });

        kakao.maps.event.addListener(kmap, "center_changed", function () {
            center_changed = true;
            // 지도의  레벨을 얻어옵니다
            // var level = map.getLevel();

            // 지도의 중심좌표를 얻어옵니다
            var latlng = kmap.getCenter();
            lati = latlng.getLat();
            longi = latlng.getLng();
            // var message = '<p>지도 레벨은 ' + level + ' 이고</p>';
            // message += '<p>중심 좌표는 위도 ' + latlng.getLat() + ', 경도 ' + latlng.getLng() + '입니다</p>';

            // var resultDiv = document.getElementById('result');
            // resultDiv.innerHTML = message;
        });
        // });
    }, [addrList, rawValues, sumedValues]);
    // }, [raw_values, sumed_values, showPanel, numDrivers, isRendered]);

    useEffect(() => {
        if (parseInt(numDrivers) > 0) {
            // @v 로 추천요청이면.
            console.log("---------------vrp_values--------------\n", sumedValues);
            console.log(`REACT_APP_VRP_HOST = ${process.env.REACT_APP_VRP_HOST}`);
            console.log(`REACT_APP_VRP_PORT = ${process.env.REACT_APP_VRP_PORT}`);
            axios
                .post(`https://${process.env.REACT_APP_VRP_HOST}:${process.env.REACT_APP_VRP_PORT}/clusters/${numDrivers}`, sumedValues)
                .then((res) => {
                    const route_info = res.data["routeinfo"];
                    const locAddrDict = drawRoutes(kmap, route_info);
                    let keys = Object.keys(route_info);
                    var vrpRawValues: VrpValue[] = [];
                    console.log("route_info", route_info);
                    for (let k of keys) {
                        vrpRawValues = vrpRawValues.concat(route_info[k]["routing"]);
                    }
                    rawValues.forEach((el: NewValue) => {
                        const vrpv = vrpRawValues.find((d) => d.key === el.key);
                        if (vrpv) {
                            el.대표순서 = vrpv.대표순서;
                            el.icon = vrpv.icon;
                        }
                        if (el.순서 && el.순서.length) {
                            for (let i = 0; i < el.순서.length; i++) {
                                el.순서[i] = `${el.대표순서}-${i + 1}`;
                            }
                        }
                    });
                    console.log("vrpRawValues", vrpRawValues, rawValues, sumedValues);
                    addMarkers(rawValues, true);
                    showPanel = false;
                    addInfoPanelOverlays(rawValues, true, showPanel);
                    generateDispatchList4TextArea(oldValues, rawValues, setToTextArea);
                    console.log('res.data["summary"]', res.data["summary"]);
                    disableVrpButton(true);
                    setToDrawer(res.data["summary"]);
                });
        }
    }, [numDrivers]);

    return <div id="map" style={{ width: "100vw", height: "100vh" }} />;
};
export default MapContainer;
