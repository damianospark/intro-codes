import React, { useState } from "react";

function App() {
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
        console.log(window.screen.availWidth);
        const w = window.screen.availWidth * 2 - 1280;
        const newWindow = window.open("", "_blank", `width=1280,height=1024,left=${w}top=0`);

        if (newWindow) {
            const type = number.startsWith("B") ? "수거" : "배송";
            const splitNumber = number.split("-")[0];
            const formattedNumber = type === "수거" ? splitNumber.replace("B", "") : splitNumber;
            const yyyymm_str = formattedNumber.slice(0, -2);
            newWindow.document.title = type === "수거" ? `반품번호 ${number}` : `주문번호 ${number}`;
            newWindow.document.body.innerHTML = `
            <iframe src='https://better.cleanb.life/tms/${type}/${yyyymm_str}/html/${number}.html' style='width:100%; height:100%; border:none;'></iframe>
            `;
            console.log(`https://better.cleanb.life/tms/${type}/${yyyymm_str}/html/${number}.html`);
        }
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
        </div>
    );
}

export default App;
