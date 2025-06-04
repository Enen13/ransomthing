import React from 'react';
import activityImg from '../outputs/activity_Ransomware_Groups_20250603_0328.png';
import monthlyImg from '../outputs/ransomware_monthly_frequency_20250603_0328.png';
import top10Img from '../outputs/Top_10_countries_attacked_20250603_0328.png';
import weekdayImg from '../outputs/weekday_attack_distribution_20250603_0328.png';
import { useNavigate } from 'react-router-dom';

function MainLeft() {
    const goToWorldMap = () => {
        window.open('http://localhost:5000/worldmap', '_blank');
    };
    const navigate = useNavigate();
    const goToAttackerPattern = () => {
        navigate('/attacker-pattern');
    };

    return (
        <div className="main-left">
        <div className="main-left-title">25-06-03 03:28:00 기준</div>
        <div className="grid">
            <div className="grid-item">
                <img
                    src={activityImg}
                    alt="랜섬웨어 그룹 주간 활동"
                    style={{ width: '100%', height: 'auto', borderRadius: '12px' }}
                />
            </div>
            <div className="grid-item">
                <img
                    src={monthlyImg}
                    alt="랜섬웨어 월간 활동"
                    style={{ width: '100%', height: 'auto', borderRadius: '12px' }}
                />
            </div>
            <div className="grid-item-3">
                <img
                    src={top10Img}
                    alt="랜섬웨어 피해 상위 10개국"
                    style={{ width: '100%', height: 'auto', borderRadius: '12px' }}
                />
            </div>
            <div className="grid-item">
                <img
                    src={weekdayImg}
                    alt="랜섬웨어 요일별 활동"
                    style={{ width: '100%', height: 'auto', borderRadius: '12px' }}
                />
            </div>
        </div>
        <div className="button-row">
            <button className="map-btn" onClick={goToWorldMap}>전세계 랜섬웨어 활동</button>
            <button className="link-btn" onClick={goToAttackerPattern}>공격자 패턴 분석</button>
        </div>
        </div>
    );
}

export default MainLeft;