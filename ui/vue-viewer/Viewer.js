import QPdfviewer from '@quasar/quasar-app-extension-qpdfviewer/src/component/QPdfviewer'
import '@quasar/extras/material-icons/material-icons.css'

import QMediaPlayer from '@quasar/quasar-ui-qmediaplayer/src/QMediaPlayer'
import '@quasar/quasar-ui-qmediaplayer/src/index.sass'
import ViewerComponent from './src/ViewerComponent.vue'

export {ViewerComponent}

export default {
  install: app => {
    app.component('QPdfviewer', QPdfviewer)
    app.use(QMediaPlayer)
    app.component('ViewerComponent', ViewerComponent)
  },
}
