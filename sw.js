// 오프라인 캐싱 없이 설치(홈화면 추가)용 최소 서비스워커
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', () => self.clients.claim());
self.addEventListener('fetch', () => {});
