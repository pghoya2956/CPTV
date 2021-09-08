import React, { useEffect } from "react";
/*global kakao*/


export default function Map() {
    useEffect(() => {
        onLoadKaKaoMap();
        //mapscript();
    }, []);

    const onLoadKaKaoMap = () => {
        window.kakao.maps.load(() => { //이거말고 데이터 변수 다 로딩되면 로드하는 함수로 바꾸기
            const mapContainer = document.getElementById("map");
            const mapOption = {
                center: new window.kakao.maps.LatLng(37.624915253753194, 127.15122688059974),
                level: 5,
            };
            const map = new window.kakao.maps.Map(mapContainer, mapOption);
            markerdata.forEach((el) => {
                // 마커를 생성합니다
                var marker = new kakao.maps.Marker({
                    //마커가 표시 될 지도
                    map: map,
                    //마커가 표시 될 위치
                    position: new kakao.maps.LatLng(el.lat, el.lng),
                });
                // 마커에 표시할 인포윈도우를 생성합니다
                var infowindow = new kakao.maps.InfoWindow({
                    content: el.title // 인포윈도우에 표시할 내용
                });

                var customOverlay = new kakao.maps.CustomOverlay({
                    position: marker.position,
                    content: marker.title,
                    xAnchor: 0.3,
                    yAnchor: 0.91
                });

                // 마커에 mouseover 이벤트와 mouseout 이벤트를 등록합니다
                // 이벤트 리스너로는 클로저를 만들어 등록합니다
                // 클로저를 만들어 주지 않으면 마지막 마커에만 이벤트가 등록됩니다
                
                
                kakao.maps.event.addListener(
                    marker,
                    "mouseover",
                    makeOverListener(map, marker, infowindow)
                );
                kakao.maps.event.addListener(
                    marker,
                    "mouseout",
                    makeOutListener(infowindow)
                );

                /*

                kakao.maps.event.addListener(marker, 'click', 
                    makeOverListener(map, marker, infowindow)
                );

                */
                
            });

            function makeOverListener(map, marker, infowindow) {
                return function () {
                    var customOverlay = new kakao.maps.CustomOverlay({
                        position: map.position,
                        content: hello,
                        xAnchor: 0.3,
                        yAnchor: 0.91
                    });

                    customOverlay.setMap(map);
                };
            }

            

            // 인포윈도우를 닫는 클로저를 만드는 함수입니다
            function makeOutListener(infowindow) {
                return function () {
                    infowindow.close();
                };
            }

            
            function makeOverListener(map, marker, infowindow){
                return function (){
                    infowindow.open(map,marker);
                }
            }
            

        });
    };
    //map

    return <div id="map" style={{ width: "100%", height: "90vh" }}></div>;
}
