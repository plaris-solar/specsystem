<template>
  <q-card style="max-width: 50vw;width:50vw;">
        <q-card-section class="bg-primary text-white row ">
            <div class="col-4"/>
            <div class="text-h4 col-4 text-center">Upload CSV Data</div>
            <div class="col-4 text-right">             
                <q-btn icon="close" flat round dense v-close-popup data-cy="upload-close-btn"/> 
            </div>
        </q-card-section>
        <q-card-section class="q-pt-none">
            <div class="row justify-center col-6 q-gutter-x-md" style="margin-top: 2vh">
                <q-file  
                        color="blue-grey" 
                        standout 
                        bottom-slots 
                        v-model="csv" 
                        clearable
                        label="Upload CSV"
                        @clear="clearFile()"
                        data-cy="upload-file-btn">
                    <template v-slot:prepend>
                    <q-icon name="attach_file" />
                    </template>
                </q-file>
                <q-select outlined
                    :options="display_docs"
                    v-model= "doc"
                    use-input
                    input-debounce="0"
                    color="blue"
                    label="Select Page" 
                    clearable 
                    data-cy="upload-doc-select"
                    @filter="filterFn">
            </q-select>
            </div>
        </q-card-section>

        <q-card-section>
            <div class="row justify-center col-6 q-gutter-x-md" style="margin-top: 2vh"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Upload" 
                 color="primary" 
                 size="lg" 
                 class="filter-btn" 
                 :disable="!doc || !csv" @click="uploadData()" 
                 data-cy="upload-upload-btn"/>
          <div style="width:2vw;"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" data-cy="upload-cancel-btn" v-close-popup />
        </q-card-actions>
    </q-card>
</template>

<script>
    import {ref, defineProps, onMounted, defineEmits} from 'vue'

    import {useRouter} from 'vue-router'

    import {postFormData} from '@/utils.js'

    export default {
        name: 'UploadCsvWindow',
    }
</script>

<script setup>

    const router = useRouter()
    const emit = defineEmits(['csvUpload'])

    const doc = ref()
    const csv = ref()

    const display_docs = ref([])

    const props = defineProps({
        docs: Array,
        doc_type: String
    })

    onMounted(() => {
        doc.value = props.doc_type
    })

    async function clearFile(){
        csv.value = null;
    }

    async function uploadData(){
        var fd = new FormData();
        fd.append('doc_type', doc.value)
        fd.append('FILE', csv.value, 'data.csv')
        await postFormData('data/csv/', fd, 'Data uploaded successfully.').then((res) => {
            if (res.status < 300){
                router.push('/ui-data/' + doc.value)
                emit('csvUpload')
            }
        })
    }

    function filterFn (val, update) {
        if (val === ''){
            update(() => {
                display_docs.value = props.docs;
            })
        return;
        }
        update(() => {
            display_docs.value = props.docs
            const needle = val.toUpperCase()
            display_docs.value = display_docs.value.filter(v => v.toUpperCase().indexOf(needle) > -1)
        })
    }
  

</script>

<style scoped>
.filter-btn {
    width: 5em;
    margin-bottom: 2vh;
}
</style>
