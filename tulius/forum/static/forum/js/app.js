import routes from './routes.js'

const NotFound = { template: '<p>Страница не найдена</p>' }

var app = new Vue({
    el: '#forum_app',
    data: {
        currentRoute: window.location.pathname,
        message: 'Привет, Vue!'
    },
    computed: {
        ViewComponent () {
            return routes[this.currentRoute] || NotFound
        }
    },
    render (h) {
        return h(this.ViewComponent)
    }
});

window.addEventListener('popstate', () => {
    app.currentRoute = window.location.pathname
})
