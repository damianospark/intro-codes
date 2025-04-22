//App.js
import React, { useState } from "react";
import NewWindow from "react-new-window";
import NewWindowContent from "./NewWindowContent";

function App() {
    const [selectedNumber, setSelectedNumber] = useState(null);

    const numbers = [
        "20231010-40600064",
        "20231016-40600001",
        "20231019-40600013",
        "20231016-40600002",
        "20231031-40600024",
        "B20231011-40600040",
        "B20231016-40600019",
        "B20231016-40600020",
        "B20231022-40600003",
        "B20231024-40600026",
        "B20231031-40600013",
    ];
    const openInNewWindow = (number) => {
        setSelectedNumber(number); // 선택된 번호를 상태로 설정
    };

    return (
        <div className="App">
            <h1>React Fetch Example</h1>
            <div className="chip-container">
                {numbers.map((number) => (
                    <button
                        key={number}
                        style={{
                            backgroundColor: number.startsWith("B") ? "#FFD2D2" : "#D2FFD2",
                            margin: "5px",
                            padding: "10px",
                            borderRadius: "20px",
                            border: "none",
                            cursor: "pointer",
                        }}
                        onClick={() => openInNewWindow(number)}
                    >
                        {number}
                    </button>
                ))}
            </div>

            {selectedNumber && (
                <NewWindow
                    title={`주문/반품 번호 ${selectedNumber}`} // 새 창의 제목
                    onUnload={() => setSelectedNumber(null)} // 새 창이 닫힐 때 상태 초기화
                    features={{ width: 1280, height: 1024, left: 100, top: 100 }} // 위치와 크기 지정
                    // 새 창의 위치와 크기 설정
                >
                    {/* 새 창에서 렌더링할 컴포넌트 */}
                    {/* 예: <NewWindowContent number={selectedNumber} /> */}
                    <NewWindowContent number={selectedNumber} />
                </NewWindow>
            )}
        </div>
    );
}

export default App;
