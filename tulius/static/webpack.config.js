const path = require('path')

module.exports = {
    entry: './app/index.js',
    output: {
        path: path.resolve(__dirname, 'app'),
        filename: 'index_bundle.js'
  }
}
