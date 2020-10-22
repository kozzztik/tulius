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
    }
}
