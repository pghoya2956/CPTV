import React, {useState, useEffect } from "react";
import axios from 'axios';
import Modal from '../Components/Modal'
import ReactPlayer from 'react-player'
/*global kakao*/



//리스트는 클릭이벤트 등록 후 클릭시 지도에 focus 해주기
export default function List() {
    const [list, setList] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchList();
        //mapscript();
    }, []);

    
    const fetchList = async () => {
        try {
            setError(null);
            setList(null);

            setLoading(true);

            
            
            
            const response = await axios.get(
                'http://192.168.0.5/data'
                
            );

            
            setList(JSON.parse(JSON.stringify(response.data)));
            console.log(response.data.num);
        } catch (e){
            setError(e);
        }
        setLoading(false);
    };

        
        list.forEach((el) => {
            if(list.dform == 1){
                list.threat = 'Stranger';
            }else if(list.dform == 2){
                list.threat = 'Wepon Detected';
            } else if (list.dform == 3) {
                list.threat = 'Violence';
            } else if (list.dform == 4) {
                list.threat = 'Threatened Voice';
            }else{
                list.threat = 'None';
            }
        });

        

    }

    const [modalOpen, setModalOpen] = useState(false);

    const openModal = () => {
        setModalOpen(true);
    }
    const closeModal = () => {
        setModalOpen(false);
    }

    if(loading) return <div>loading</div>;
    if (error) return <div>error</div>;
    if(!list) return null;


    return (
        <div class="list-group list-group-flush border-bottom scrollarea">
            {list.map(elem=>(

                <a key={elem.num} id="openModalBtn" class="list-group-item list-group-item-action py-3 lh-tight" aria-current="true">
                    <div class="d-flex w-100 align-items-center justify-content-between">
                        <strong class="mb-1">{elem.title}</strong>
                        <p>{elem.threat}</p>
                    </div>
                    <div class="col-10 mb-1 small">최근 탐지일 : {elem.dtime}</div>
                    <button class="btn btn-primary" onClick={openModal}>
                        영상
                    </button>
                    
                    
                </a>
                

            ))}
            <Modal open={modalOpen} close={closeModal} header="영상">
                <div className = 'player-wrapper'>
                    <ReactPlayer
                    className='react-player fixed-bottom'
                    url='videos/test.MP4'
                    width='100%'
                    height='100%'
                    controls ={true}
                    />
                </div>

            </Modal>
        </div>
        

    ); 
}
