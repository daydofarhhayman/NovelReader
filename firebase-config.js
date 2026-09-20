// =============================================================================
// Firebase 專案設定檔 (firebase-config.js)
// 說明：請將您在 Firebase Console 建立的 Web 應用程式設定填入下方。
//      一般讀者無需看到或輸入此設定，只需在首頁點擊「Google 登入」即可。
// =============================================================================

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// 自動初始化 Firebase (若已填寫正式金鑰)
if (typeof firebase !== 'undefined' && firebaseConfig.apiKey && firebaseConfig.apiKey !== "YOUR_API_KEY") {
  try {
    if (!firebase.apps.length) {
      firebase.initializeApp(firebaseConfig);
      console.log("✅ Firebase 雲端服務已由後台設定檔成功初始化！");
    }
  } catch (err) {
    console.warn("⚠️ Firebase 初始化異常:", err);
  }
}
