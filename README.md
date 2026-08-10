# AI Travel Guide Website

### 

### 專題簡介



本專題是一個「AI 輔助旅遊景點推薦平台」範例，使用 Bootstrap 製作 RWD 前端頁面，使用 Vue.js 呼叫 Flask API，並以 SQLite 儲存景點與分類資料。



系統可以瀏覽景點、查詢景點、查看景點詳細內容、管理景點資料，並在管理頁顯示統計圖表。



#### 🛠️ 使用技術 (Technologies Used)



前端技術 (Frontend)



* HTML5 / CSS3：響應式頁面佈局、自訂 UI 樣式（統一抽離至 專案.css）。



* JavaScript (ES6+)：前端非同步資料處理與 DOM 控制。



* Vue 3 (CDN)：漸進式 JavaScript 框架，實現雙向資料繫結、狀態管理與動態列表渲染。



* Axios：基於 Promise 的 HTTP 庫，負責與後端 Flask API 進行跨域資料傳輸。



* Bootstrap 5：提供 Grid 網格系統、Modal 彈窗、Card 元件與基礎響應式樣式。



* 後端技術 (Backend)



&nbsp;               Python 3：後端核心開發語言。



&nbsp;               Flask：輕量級 Web API 框架。



&nbsp;               Flask-CORS：處理前端與後端不同 Port 時的跨域資源共享 (CORS)。



* 資料庫與資料格式 (Database \& Data Format)



&nbsp;              SQLite3：輕量級關聯式資料庫，儲存景點與使用者收藏紀錄。



&nbsp;             JSON (花蓮.json)：初始化景點種子資料庫，並提供雙向資料同步備份。

#### 

#### 💻 系統功能說明 (System Features)





* 首頁導覽 (index.html / 歡迎頁面.html)



&nbsp;                           1. Hero 滿版視覺橫幅：高質感視覺吸引使用者。



&nbsp;                           2. 能夠清楚引導使用者到其他分頁的導覽列。



* 景點列表與即時收藏 (test2.html)

&nbsp;                          1. 關鍵字即時搜尋與分類過濾：使用者輸入關鍵字或選擇區域時，Vue 會即時進行前端資料過濾。



&nbsp;                          2. 景點詳細資訊 Modal：點擊景點卡片可彈出 Modal 檢視開放時間、門票、導航等完整細節。



&nbsp;                          3. 網格卡片佈局：展示全花蓮景點，圖片採用固定比例與 object-fit: cover 避免拉伸。



&nbsp;                          4. 一鍵收藏功能：卡片右上角設有愛心按鈕，點擊觸發 API 切換收藏狀態（即時變更按鈕樣式與後端資料）。



* 我的收藏管理 (favorite.html)



&nbsp;                           1. 個人化收藏清單：串接後端 API，顯示所有收藏的景點。



&nbsp;                           2. 收藏時間紀錄：卡片明確標示 collected\_at 收藏時間。



&nbsp;                           3.一鍵移除與快速跳轉：點擊愛心可立即取消收藏並刷清清單；底部設有「查看景點」按鈕可快速連回景點列表。



* 後台景點管理 (景點管理.html)



&nbsp;                            1. 新增景點：提供表單建立新景點，自動生成 ID（例 HL-ATT-XXXXX）與時間戳，同時寫入 SQLite 與 花蓮.json。



&nbsp;                            2. 刪除景點：可從資料庫中硬刪除指定景點，並透過級聯（CASCADE）自動清空對應的收藏紀錄。



#### 專案畫面截圖



* 首頁



<img width="1911" height="1028" alt="首頁" src="https://github.com/user-attachments/assets/0520e77d-f3f5-4787-93e7-2183f87b4db5" />



* 景點列表

<img width="1834" height="1039" alt="景點列表" src="https://github.com/user-attachments/assets/e6d02166-b78c-48a8-a8ed-a4c5357822e7" />



* 景點詳細內容


<img width="897" height="841" alt="景點詳細內容" src="https://github.com/user-attachments/assets/aae4ff9c-731f-46f8-883e-4cb9c2fc8847" />



* 景點管理


<img width="1727" height="984" alt="景點管理" src="https://github.com/user-attachments/assets/1cb5838c-e274-481b-ad75-89f699bb5d25" />




* 我的收藏


<img width="1843" height="1025" alt="我的收藏" src="https://github.com/user-attachments/assets/11a3a007-778b-4fba-b753-f6887116ff3b" />


* 統計圖表


<img width="1876" height="713" alt="統計圖表" src="https://github.com/user-attachments/assets/7ddb5e96-85ca-4ac6-b5e5-8e6d6a50f0ba" />



* RWD檢查截圖





* 桌機寬度1200px



<img width="1296" height="1043" alt="桌機寬度1200px" src="https://github.com/user-attachments/assets/c7193fed-8ae7-4820-821e-919c14535439" />



* 平板寬度768px


<img width="814" height="1037" alt="平板寬度768px" src="https://github.com/user-attachments/assets/732df6f3-2d91-40e6-8951-d7f6dfdaad7e" />





* 手機寬度375px



<img width="641" height="723" alt="手機寬度375px" src="https://github.com/user-attachments/assets/60396552-0e23-4051-bccf-3d4ec748fde0" />



#### 🗄️ 資料庫設計說明 (Database Design)



系統採用 SQLite3，包含兩張核心資料表：attractions (景點主表) 與 favorites (收藏關聯表)。



1.attractions 景點資料表



<img width="732" height="406" alt="attractions 景點資料表" src="https://github.com/user-attachments/assets/91b54c2e-1a5f-4042-88b9-cbc2e7fc3b50" />





2.favorites 收藏資料表

<img width="942" height="523" alt="favorites 收藏資料表" src="https://github.com/user-attachments/assets/df20ed2c-46bf-4289-a956-e0a712303d57" />


#### 







3\.資料表關聯



&nbsp;   1 對多 (1:N) 關聯：一位使用者可以收藏多個景點，一個景點也可以被多個使用者收藏（透過 favorites 做為中間連結表）。



&nbsp;       唯一性限制 (UNIQUE)：UNIQUE(user\_id, attraction\_id)，確保同一位使用者不會重複收藏同一個景點。



&nbsp;       外鍵級聯刪除 (ON DELETE CASCADE)：當 attractions 中的某個景點被刪除時，favorites 資料表中所有對應該景點的收藏紀錄會自動被連帶清除，確保資料完整性。



#### 📡 API 說明 (API Documentation)



1\. 取得所有景點列表


<img width="848" height="638" alt="取得所有景點列表" src="https://github.com/user-attachments/assets/a4fa6995-e429-461f-bb62-ccb6026f40e6" />



2\. 新增景點


<img width="855" height="688" alt="新增景點" src="https://github.com/user-attachments/assets/4a7fe436-1b91-4973-84d1-062dd7c78a83" />



3\. 刪除景點


<img width="862" height="632" alt="刪除景點" src="https://github.com/user-attachments/assets/75a8f62c-5be3-4fd1-b62a-1fd8df3295f8" />



4\. 切換景點收藏狀態 


<img width="864" height="656" alt="切換景點收藏狀態" src="https://github.com/user-attachments/assets/04e8fcc6-45c7-4551-ba51-79780d092a79" />



5\. 刪除指定收藏


<img width="859" height="649" alt="刪除指定收藏" src="https://github.com/user-attachments/assets/1e5e2113-4e93-4105-894f-28406de03b75" />



6\. 取得使用者收藏清單


<img width="854" height="704" alt="取得使用者收藏清單" src="https://github.com/user-attachments/assets/d3b4c408-8b1c-4814-acea-3473ebba81c9" />


#### ⚙️ 安裝與執行方式 (Installation \& Setup)





1\. 建立虛擬環境



&nbsp;     python -m venv .venv



2\.安裝套件

&nbsp;     

&nbsp;    .pip install flask

&nbsp;    .pip install flask flask-cors



3\.啟動 Flask



&nbsp;    .venv\\Scripts\\python app1.py



4\.開啟網站



&nbsp;    http://127.0.0.1:5000



5\.前端開啟方式



&nbsp;    直接使用瀏覽器開啟專案資料夾中的 index.html（或使用 VS Code 的 Live Server 套件開啟），即可開始體驗「花蓮旅遊景點導覽與收藏系統」！























































