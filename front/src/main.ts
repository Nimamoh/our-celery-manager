import './assets/main.css'
import 'primevue/resources/themes/lara-light-indigo/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

import { createApp, ref, type Ref } from 'vue'

import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';

import App from './App.vue';
import router from './router'

import { Configuration, DefaultApi } from './generated/api';

import type { Settings } from './models/settings.model';

const app = createApp(App)

app.use(router)
app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)


// XXX Attention: si ça prend du temps la page reste blanche
const { api_url, api, info } = await _init_appwide_provides()

app.provide('api_url', api_url)
app.provide('api', api)
app.provide('info', info)


app.mount('#app')

async function _init_appwide_provides() {
    const api_url: string = import.meta.env.VITE_API_URL

    const api_conf = new Configuration({
        basePath: api_url,
        middleware: [],
    })
    const api = new DefaultApi(api_conf);

    let info: Ref<Partial<Settings>> = ref({ application_name: 'Our celery manager' });
    info.value = await api.infoInfoGet()

    return {
        api_url,
        api,
        info,
    }
}