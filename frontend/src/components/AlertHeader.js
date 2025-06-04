import React, { useEffect, useState } from 'react';
import axios from 'axios';

function AlertHeader() {
  const [alerts, setAlerts] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);

  useEffect(() => {
    axios.get('/get_alerts')
      .then(res => {
        setAlerts(res.data.alerts || []);
      })
      .catch((err) => {
        setAlerts([]);
      });
  }, []);

  useEffect(() => {
    if (alerts.length === 0) return;

    setCurrentIdx(0); // 알림이 바뀌면 처음부터 보여주기

    const interval = setInterval(() => {
      setCurrentIdx(prevIdx => (prevIdx + 1) % alerts.length);
    }, 6000);

    return () => clearInterval(interval);
  }, [alerts]);

  return (
    <div className="sub-header">
      <span className="blinking-text">
        ⚠️ <span className="alert-keyword">랜섬웨어</span> 탐지 알림 ⚠️
      </span>
      <ul>
        {alerts.length > 0 && (
            <li
            key={currentIdx}
            dangerouslySetInnerHTML={{
                __html: alerts[currentIdx]
                ?.replace(/🗓/g, '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🗓')
                ?.replace(/📌/g, '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;📌'),
            }}
            />
        )}
      </ul>
    </div>
  );
}

export default AlertHeader;