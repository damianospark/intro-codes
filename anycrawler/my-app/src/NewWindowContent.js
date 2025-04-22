//NewWindowContent.js
import React, { useEffect, useState } from "react";

function NewWindowContent({ number }) {
  const [htmlContent, setHtmlContent] = useState("");
  const type = number.startsWith("B") ? "수거" : "배송";

  useEffect(() => {
    const fetchData = async () => {
      console.log("fetchData 실행 중...");

      const splitNumber = number.split("-")[0];
      const formattedNumber = type === "수거" ? splitNumber.replace("B", "") : splitNumber;
      const yyyymm_str = formattedNumber.slice(0, -2);

      const url = `https://better.cleanb.life/tms/${type}/${yyyymm_str}/html/${number}.html`;
      const options = {
        method: "GET",
      };

      try {
        const response = await fetch(url, options);
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        let data = await response.text();

        // 'html' 폴더까지의 경로 추출 및 href, src 속성 수정
        const basePath = url.substring(0, url.lastIndexOf("/html") + 1);
        const modifiedData = data.replace(/href="\.\.\//g, `href="${basePath}`).replace(/src="\.\.\//g, `src="${basePath}`);

        setHtmlContent(modifiedData);
      } catch (error) {
        console.error("Fetching error:", error);
      }
    };

    fetchData();
  }, [number, type]);
  useEffect(() => {
    if (htmlContent) {
      const newWindowDocument = document.createElement("div");
      newWindowDocument.innerHTML = htmlContent;

      // 외부 링크에 target="_blank" 추가
      const links = newWindowDocument.querySelectorAll("a[href^='http']");
      links.forEach((link) => {
        link.setAttribute("target", "_blank");
      });

      // 탭 버튼 클릭 이벤트에서 버블링 중지
      const tabs = newWindowDocument.querySelectorAll(".nav-item .nav-link");
      tabs.forEach((tab) => {
        tab.addEventListener("click", (event) => {
          event.stopPropagation();
        });
      });

      setHtmlContent(newWindowDocument.innerHTML);
    }
  }, [htmlContent]);
  // useEffect(() => {
  //     // 탭 기능 활성화
  //     const preventDefaultForTabs = (event) => {
  //         event.preventDefault();
  //         if (window.opener) {
  //             window.opener.focus();
  //         }
  //     };
  //     const activateTabs = () => {
  //         const tabs = document.querySelectorAll(".nav-item .nav-link");
  //         const tabPanes = document.querySelectorAll(".tab-content .tab-pane");

  //         tabs.forEach((tab, index) => {
  //             tab.addEventListener("click", (event) => {
  //                 preventDefaultForTabs(event); // Prevent default behavior
  //                 tabs.forEach((t) => t.classList.remove("active"));
  //                 tabPanes.forEach((pane) => pane.classList.remove("active"));
  //                 tab.classList.add("active");
  //                 tabPanes[index].classList.add("active");
  //             });
  //         });
  //     };

  //     // HTML 컨텐츠가 변경될 때마다 탭 기능을 활성화
  //     if (htmlContent) {
  //         activateTabs();
  //     }
  // }, [htmlContent]);

  return <div dangerouslySetInnerHTML={{ __html: htmlContent }} />;
}

export default NewWindowContent;
