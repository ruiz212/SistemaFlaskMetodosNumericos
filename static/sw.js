const CACHE_NAME = 'suite-num-v1';
const ASSETS = [
  '/',
  '/static/css/base.css',
  '/static/css/index.css',
  '/static/js/main.js',
  '/static/manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((res) => res || fetch(e.request))
  );
});
