import FileUploadComponent from './src/FileUploadComponent.vue'

export {FileUploadComponent}

export default {
  install(app) {
    app.component('FileUploadComponent', FileUploadComponent)
  },
}
