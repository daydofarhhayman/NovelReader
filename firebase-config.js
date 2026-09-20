// =============================================================================
// Firebase 專案設定檔 (firebase-config.js)
// 說明：請將您在 Firebase Console 建立的 Web 應用程式設定填入下方。
//      一般讀者無需看到或輸入此設定，只需在首頁點擊「Google 登入」即可。
// =============================================================================

const firebaseConfig = {
  apiKey: "AIzaSyCC3YSw4v1IsQmZzuEpxP6crQpgDKZ8IZw",
  authDomain: "novelreader-dec08.firebaseapp.com",
  projectId: "novelreader-dec08",
  storageBucket: "novelreader-dec08.firebasestorage.app",
  messagingSenderId: "948383757506",
  appId: "1:948383757506:web:939571345164b56059f75b",
  measurementId: "G-2LQ2FQQPPT"
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
