// App.js
import React, { useState, useEffect } from "react";
import "./App.css"; // 스타일 시트 임포트

function IframeComponent() {
    const [iframeHeight, setIframeHeight] = useState(window.innerHeight);
    const url = "https://better.cleanb.life/tms/배송/202310/html/shipping-20231009-23261185.html";

    useEffect(() => {
        const handleResize = () => {
            setIframeHeight(window.innerHeight);
        };

        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    return (
        <div className="iframeContainer">
            <h1>External HTML in Iframe</h1>
            <iframe src={url} style={{ width: "100%", height: iframeHeight, border: "none" }} title="External Content" />
        </div>
    );
}

export default IframeComponent;
