import React, { useState, useRef, useEffect } from 'react';

function Sidebar() {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: (
        <>
          안녕하세요! 랜섬웨어 정보 챗봇입니다.<br />
          다음 명령어를 사용하세요:<br />
          - 그룹 검색: "검색 [그룹명]"<br />
          - 공격 순위: "공격 순위"<br />
          - 오늘의 공격: "오늘 공격"
        </>
      ),
    },
  ]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const chatArea = chatEndRef.current?.parentNode;
    if (chatArea) {
      chatArea.scrollTop = 0;
    }
  }, [messages]);

  // 명령어 파싱
  const parseCommand = (text) => {
    if (text.startsWith('검색 ')) {
      return { command: 'search', query: text.replace('검색 ', '').trim() };
    }
    if (text === '공격 순위') {
      return { command: 'attack_rank', query: '' };
    }
    if (text === '오늘 공격') {
      return { command: 'today_attacks', query: '' };
    }
    return { command: 'unknown', query: text };
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', text: inputValue }]);
    const { command, query } = parseCommand(inputValue);

    try {
      const res = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, query }),
      });
      const data = await res.json();

      // 여기서 콘솔에 출력
      console.log('API 응답 데이터:', data);

      if (data.error) {
        setMessages((prev) => [
          ...prev,
          { role: 'bot', text: data.error },
        ]);
      } else if (data.data) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'bot',
            text: Array.isArray(data.data)
              ? data.data
                  .map((item, idx) => {
                    // rank, name, count가 모두 있으면 (공격 순위)
                    if ('rank' in item && 'name' in item && 'count' in item) {
                      return `${item.rank}. ${item.name} (${item.count}건)`;
                    }
                    // domain, group이 있으면 (오늘 공격)
                    if ('domain' in item && 'group' in item) {
                      return `도메인: ${item.domain} / 그룹: ${item.group}`;
                    }
                    // 기타 객체는 JSON 문자열로 출력
                    return JSON.stringify(item);
                  })
                  .join('\n')
              : data.data,
          },
        ]);
      } else if (data.fields) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'bot',
            text: Array.isArray(data.fields)
              ? data.fields
                  .map(
                    (item) => `${item.name}: ${item.value}`
                  )
                  .join('\n')
              : data.fields,
          },
        ]);
      } else if (data.result) {
        setMessages((prev) => [
          ...prev,
          { role: 'bot', text: data.result },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: 'bot', text: '알 수 없는 응답입니다.' },
        ]);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: 'bot', text: '서버 오류가 발생했습니다.' },
      ]);
    }
    setInputValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <aside className="sidebar">
      <div className="search-box">
        <input
          type="text"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="검색"
          className="search-input"
        />
        <button className="search-icon" onClick={handleSend}>🔍</button>
      </div>
        <div className="chat-area">
          <div ref={chatEndRef} />
          {messages.slice().reverse().map((msg, idx) => (
            <div
              key={idx}
              className={`chat-bubble-messenger ${msg.role}`}
            >
              {typeof msg.text === 'string'
              ? msg.text.split('\n').map((line, i) => <div key={i}>{line}</div>)
              : msg.text}
            </div>
          ))}
        </div>
    </aside>
  );
}

export default Sidebar;