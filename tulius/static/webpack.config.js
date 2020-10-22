const path = require('path')

module.exports = {
    entry: './app/index.js',
    mode: 'development',
    output: {
        path: path.resolve(__dirname, 'app'),
        filename: 'index_bundle.js'
    },
    devServer: {
        port: 9000,
        headers: {"Access-Control-Allow-Origin": "*"},
    },
    resolve: {
        alias: {
          // If using the runtime only build
          'vue$': path.resolve(__dirname, 'common/js/vue.js') // 'vue/dist/vue.runtime.common.js' for webpack 1
        }
    }
}
