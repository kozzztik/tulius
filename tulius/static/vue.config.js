module.exports = {
    publicPath: '/static/',
    pages: {
        app: {
            entry: 'app/index.js',
            template: 'app/index.html',
        }
    },
    runtimeCompiler: true,
    filenameHashing: false,
    lintOnSave: false,
    devServer: {
        port: 9000,
        headers: {"Access-Control-Allow-Origin": "*"},
    },
    // удаление плагинов webpack связанных с HTML
    chainWebpack: config => {
        config.plugins.delete('html')
        config.plugins.delete('preload')
        config.plugins.delete('prefetch')
    },
}