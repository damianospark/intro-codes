import { useEffect } from "react";

import * as dfd from "danfojs";
//import specific methods/classes
// import fs from fs;
// const fs = require("fs");
const Papa = require("papaparse");
// papaParse : https://joshtronic.com/2022/05/15/how-to-convert-csv-to-json-in-javascript/
// multiline str : https://stackoverflow.com/questions/805107/creating-multiline-strings-in-javascript
// danfo dataframe : https://blog.tensorflow.org/2020/08/introducing-danfo-js-pandas-like-library-in-javascript.html
// const file = '/path/to/your/file.csv';
const csvData = `순위	이름	주소	lat	lan
`

const jsonData = Papa.parse(csvData, { header: true, delimiter: "\t" });
console.log(jsonData);
const df = new dfd.DataFrame(jsonData.data);

df.print();

declare global {
    interface Window {
        kakao: any;
    }
}
let map: any;
let marker: any;

// const kakao = window;
// const map: {window.kakao.maps.Map}

function initMap() {
    const container = document.getElementById("map"); //지도를 담을 영역의 DOM 레퍼런스
    const options = {
        //지도를 생성할 때 필요한 기본 옵션
        center: new window.kakao.maps.LatLng(37.514564, 127.105919), //지도의 중심좌표.
        level: 3, //지도의 레벨(확대, 축소 정도)
    };
    map = new window.kakao.maps.Map(container, options); //지도 생성 및 객체 리턴    }, []);
}

function addMarkers() {
    //마커가 표시 될 위치
    let markerPosition = new window.kakao.maps.LatLng(
        37.514564,
        127.105919
        // 이부분의 위,경도 또한 가끔 가는 카페입니다.. 놀라지마시길..!
    );

    // 마커를 생성
    marker = new window.kakao.maps.Marker({
        position: markerPosition,
    });

    // 마커를 지도 위에 표시
    marker.setMap(map);
}

function addInfoPanel() {
    var iwContent =
            '<div style="padding:5px;">Hello World! <br><a href="https://map.window.kakao.com/link/map/Hello World!,33.450701,126.570667" style="color:blue" target="_blank">큰지도보기</a> <a href="https://map.window.kakao.com/link/to/Hello World!,33.450701,126.570667" style="color:blue" target="_blank">길찾기</a></div>', // 인포윈도우에 표출될 내용으로 HTML 문자열이나 document element가 가능합니다
        iwPosition = new window.kakao.maps.LatLng(37.514564, 127.105919); //인포윈도우 표시 위치입니다

    // 인포윈도우를 생성합니다
    var infowindow = new window.kakao.maps.InfoWindow({
        position: iwPosition,
        content: iwContent,
    });

    // 마커 위에 인포윈도우를 표시합니다. 두번째 파라미터인 marker를 넣어주지 않으면 지도 위에 표시됩니다
    infowindow.open(map, marker);
}

const MapContainer = () => {
    useEffect(() => {
        initMap();
        addMarkers();
        addInfoPanel();
    }, []);

    return <div id="map" style={{ width: "100vw", height: "100vh" }} />;
};
export default MapContainer;
