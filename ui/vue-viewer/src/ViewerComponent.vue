<script setup lang="ts">
import {onMounted, ref} from 'vue'
import {useVModel} from '@vueuse/core'
import {useI18n} from 'vue-i18n'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
  axios: {
    type: Object,
    required: true,
  },
  tab: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])
const model = useVModel(props, 'modelValue', emit)
const {t} = useI18n()

const textViewer = ref(false)
const textDialog = ref<{label: string; text: string}>()

const pdfViewer = ref(false)
const pdfSource = ref<string>()

const imageViewer = ref(false)
const imageDialog = ref<{label: string; imageSource: string}>()

const mediaViewer = ref(false)
const mediaSource = ref<[{src: string; type: string}]>()

onMounted(async () => {
  if (props.tab) {
    let url = `/viewer/?url=${model.value}&label=${props.label}`
    const w = window.open(url, '_blank')
    if (w) w.focus()
  } else {
    const response = await props.axios.get(model.value, {
      responseType: 'blob',
    })
    const blob = new Blob([response.data], {
      type: response.headers['content-type'],
    })
    const url = URL.createObjectURL(blob)
    const downloadAsFile = () => {
      const link = document.createElement('a')
      link.setAttribute('download', props.label)
      link.href = url
      link.click()
      URL.revokeObjectURL(link.href)
    }
    switch (response.headers['content-type']) {
      case 'text/csv':
      case 'text/plain':
        // TODO Create a size constant.
        if (Number(response.headers['content-length']) < 50000) {
          blob.text().then(text => {
            textDialog.value = {label: props.label, text: text}
            textViewer.value = true
          })
        } else {
          downloadAsFile()
        }
        break
      case 'application/pdf': {
        pdfSource.value = url
        pdfViewer.value = true
        break
      }
      case 'image/jpeg':
      case 'image/png':
      case 'image/gif':
      case 'image/svg+xml':
        imageDialog.value = {label: props.label, imageSource: url}
        imageViewer.value = true
        break
      case 'video/mp4': {
        mediaSource.value = [{src: url, type: 'video/mp4'}]
        mediaViewer.value = true
        break
      }
      default: {
        downloadAsFile()
      }
    }
  }
})
</script>

<template>
  <q-dialog v-model="textViewer">
    <q-card>
      <q-card-section>
        <div class="text-h6">{{ textDialog!.label }}</div>
      </q-card-section>

      <q-card-section class="q-pt-none">{{ textDialog!.text }}</q-card-section>

      <q-card-actions align="right">
        <q-btn v-close-popup :label="t('label.close')" flat color="primary" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="pdfViewer" full-height full-width>
    <q-pdfviewer :src="pdfSource" type="html5" />
  </q-dialog>

  <q-dialog v-model="imageViewer">
    <q-card>
      <q-card-section>
        <div class="text-h6">{{ imageDialog!.label }}</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-img :src="imageDialog!.imageSource" />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn v-close-popup :label="t('label.close')" flat color="primary" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="mediaViewer" full-height full-width>
    <!-- TODO No buttons visible in the player. -->
    <q-media-player type="video" :sources="mediaSource" :autoplay="true" :show-big-play-button="false" />
  </q-dialog>
</template>
