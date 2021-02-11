Vue.use(Vuex)

const store = new Vuex.Store({
    state: {
        count: 7
    },
    mutations: {
        increment(state) {
            state.count++
        }
    }
})