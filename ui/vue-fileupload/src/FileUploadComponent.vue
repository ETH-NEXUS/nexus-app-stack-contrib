<script setup lang="ts">
import {PropType, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {Notify, ValidationRule} from 'quasar'
import {File, Files} from '../types/api'

const {t} = useI18n()

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  files: {
    type: Object as PropType<Files>,
    validator: v => v === undefined || typeof v === 'object',
    required: true,
  },
  maxFiles: {
    type: Number,
    default: () => 10,
  },
  acceptedMimeTypes: {
    type: Array<string>,
    default: () => [
      'application/pdf',
      'image/gif',
      'image/jpeg',
      'image/png',
      'image/svg+xml',
      'text/csv',
      'text/plain',
      'video/mp4',
    ],
  },
  disable: {
    type: Boolean,
    default: () => false,
  },
  readonly: {
    type: Boolean,
    default: () => false,
  },
  hint: {
    type: String,
    required: true,
  },
  rules: {
    type: Object as PropType<((value: ValidationRule) => boolean)[]>,
    default: () => {
      return []
    },
  },
  tabViewer: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits<{
  (event: 'addFile', files: Files, progress: (fraction: number) => void, done: (file: File) => void): void
  (event: 'downloadFile', file: File): void
  (event: 'removeFile', file: File, done: () => void): void
}>()

const files = ref(props.files)
const initialFiles = files.value === null ? [] : [...files.value]
const uploadFiles = ref<[] | undefined>(undefined)
const maxFiles = ref(props.maxFiles - Object.keys(initialFiles).length)
const maxFileSize = ref(Number(import.meta.env.VITE_APP_HARD_UPLOAD_SIZE_LIMIT) / props.maxFiles)
const confirm = ref(false)
const key = ref<number>()

const progress = ref<number[]>([])

const rejected = (files: Array<{failedPropValidation: string; file: File}>) => {
  files.forEach(item => {
    Notify.create({
      message: `${t('error.file_rejected')}: ${item.file.name}`,
      caption: t(`error.${item.failedPropValidation.replaceAll('-', '_')}`),
      icon: 'warning',
      color: 'warning',
    })
  })
}

const add = () => {
  emit(
    'addFile',
    uploadFiles.value,
    (fraction: number) => {
      let fileCount = uploadFiles.value ? uploadFiles.value.length : 0
      if (fraction == 1) {
        uploadFiles.value = undefined
        maxFiles.value -= fileCount
        progress.value = []
      } else {
        let index = Math.floor(fraction * fileCount)
        for (let i = 0; i < index; i++) {
          progress.value[i] = 1
        }
        progress.value[index] = fraction * fileCount - index
      }
    },
    (file: File) => {
      files.value.push(file)
    }
  )
}

const confirmRemove = (k: number) => {
  key.value = k
  confirm.value = true
}

const remove = (k: number) => {
  const file = files.value[k]
  emit('removeFile', file, () => {
    delete initialFiles[k]
    delete files.value[k]
    maxFiles.value += 1
  })
}

const download = (file: File) => {
  emit('downloadFile', file)
}

const newRules = props.rules.map(f => () => f(files.value))
</script>

<template>
  <div class="full-width text-left">{{ label }}</div>

  <!-- TODO 'placeholder' instead of 'label' would be nice but does not work. -->
  <q-file
    v-if="!readonly"
    v-model="uploadFiles"
    multiple
    counter
    :max-files="maxFiles"
    :max-file-size="maxFileSize"
    :accept="acceptedMimeTypes.join(', ')"
    :label="uploadFiles === undefined ? t('label.click_to_add_files') : undefined"
    :disable="disable"
    :readonly="progress.length > 0"
    outlined
    lazy-rules
    :rules="newRules"
    @rejected="rejected">
    <template #file="{index, file}">
      <q-chip
        class="q-my-xs"
        square
        :removable="progress.length === 0"
        @remove="uploadFiles!.splice(index, 1)">
        <q-linear-progress
          class="absolute-full full-height rounded-borders"
          :value="progress[index]"
          color="light-blue-5"
          track-color="grey-2"
          stripped />
        <div class="ellipsis relative-position">{{ file.name }}</div>
      </q-chip>
    </template>

    <template #prepend>
      <q-icon name="cloud_upload" />
    </template>
    <template #after>
      <q-btn
        round
        dense
        flat
        color="red"
        icon="send"
        :disable="readonly || uploadFiles === undefined"
        :loading="progress.length > 0"
        @click="add" />
    </template>
    <template #hint>{{ hint }}</template>
  </q-file>

  <div v-if="Object.keys(initialFiles).length > 0" class="q-my-xs inline bg-grey-4 rounded-borders">
    <span v-if="!readonly" class="q-pl-xs">{{ t('label.old_uploads') }}</span>
    <span v-for="(file, k) in initialFiles" :key="k">
      <q-chip
        v-if="file"
        clickable
        :removable="!readonly"
        color="teal"
        text-color="white"
        icon="description"
        @remove="confirmRemove(k)"
        @click="download(file)">
        {{ file.name }}
      </q-chip>
    </span>
  </div>

  <div
    v-if="files && Object.keys(files).length > Object.keys(initialFiles).length"
    class="q-my-xs inline bg-grey-4 rounded-borders">
    <span class="q-pl-xs">{{ t('label.new_uploads') }}</span>
    <span v-for="(file, k) in files" :key="k">
      <q-chip
        v-if="initialFiles[k] === undefined && file"
        :key="k"
        clickable
        removable
        color="green"
        text-color="white"
        icon="description"
        @remove="confirmRemove(k)"
        @click="download(file)">
        {{ file.name }}
      </q-chip>
    </span>
  </div>

  <q-dialog v-model="confirm" persistent>
    <q-card>
      <q-card-section class="row items-center">
        <q-avatar icon="delete" color="red" text-color="white" />
        <span v-if="files[key!]" class="q-ml-sm">
          {{ `${t('message.really_remove')} ${files[key!].name}` }}
        </span>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn v-close-popup flat :label="t('label.cancel')" color="primary" />
        <q-btn v-close-popup flat :label="t('label.remove')" color="primary" @click="remove(key!)" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
