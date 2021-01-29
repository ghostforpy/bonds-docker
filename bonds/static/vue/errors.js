Vue.component('errors', {
    props: ['errors'],
    template: ` <div>
                    <p>Ошибка</p>
                    <ul>
                        <li v-for="error in errors">
                            <div v-html="error">
                              
                            </div>
                        </li>
                    </ul>   
                </div>`
})