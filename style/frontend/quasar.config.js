const { configure } = require('quasar/wrappers')

module.exports = configure(function (ctx) {
  return {
    boot: [
      'pinia'
    ],

    css: [
      'app.scss',
      'new-design.css'
    ],

    extras: [
      'material-icons'
    ],

    build: {
      target: { browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'] },
      vueRouterMode: 'history',
      
    },

    devServer: {
      port: 9200,
      open: false,
      proxy: {
        '/api': {
          target: 'http://localhost:3000',
          changeOrigin: true,
        },
        '/uploads': {
          target: 'http://localhost:3000',
          changeOrigin: true,
        }
      }
    },

    framework: {
      config: {},
      plugins: ['Notify', 'Dialog', 'Loading']
    },

    ssr: {
      pwa: false,
      prodPort: 3000,
      middlewares: ['render'],
      extendSSRWebserverConf (esbuildConf) {},
      manualPostSerialization: false
    },

    pwa: {
      workboxMode: 'GenerateSW',
      injectPwaMetaTags: true,
      swFilename: 'sw.js',
      manifestFilename: 'manifest.json',
      useCredentialsForManifestTag: false
    },

    capacitor: {
      hideSplashscreen: true
    },

    electron: {
      bundler: 'packager',
      packager: {},
      builder: {
        appId: 'cloudland-frontend'
      }
    },

    bex: {
      contentScripts: ['my-content-script']
    }
  }
})
