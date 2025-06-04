import React from 'react';
import patternImg from '../outputs/correlation_plot.png'; // 이미지 파일명에 맞게 경로 수정

function AttackerPattern() {
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = `${process.env.PUBLIC_URL}/analyzed_step4.csv`;
    link.download = 'analyzed_step4.csv'; // 다운로드 시 저장될 파일 이름
    link.click();
  };

  return (
    <div style={{ background: '#232526', minHeight: '100vh', padding: '0', margin: '0' }}>
      <div style={{
        background: '#b30000',
        color: '#fff',
        fontSize: '2rem',
        fontWeight: 'bold',
        textAlign: 'center',
        padding: '1.2rem 0'
      }}>
        RansomThing
      </div>
      <div style={{
        background: '#ff6f6f',
        color: '#fff',
        fontSize: '1.5rem',
        fontWeight: 'bold',
        textAlign: 'center',
        padding: '0.8rem 0'
      }}>
        공격자 패턴 분석
      </div>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginTop: '2rem'
      }}>
        <img
          src={patternImg}
          alt="공격자 패턴 분석"
          style={{ maxWidth: '80vw', borderRadius: '12px', background: '#fff', padding: '1rem' }}
        />
        <div style={{
          color: '#fff',
          fontSize: '1rem',
          marginTop: '1.5rem',
          textAlign: 'center',
          marginBottom: '0.5rem'
        }}>
          해당 자료는 threat actor들의 채팅내역과 <span style={{ color: '#ffb3b3' }}>ransomnote</span>의 공격성과 감수성 지수를 분석하여 성향별로 5집단으로 나눈 그래프입니다
        </div>
        <button style={{
          background: '#ff6f6f',
          color: '#fff',
          fontSize: '1rem',
          padding: '0.5rem 1rem',
          borderRadius: '10px',
          cursor: 'pointer',
          marginTop: '1rem',
          marginBottom: '1.5rem'
        }} onClick={handleDownload}>csv파일 다운로드</button>
      </div>
    </div>
  );
}

export default AttackerPattern;