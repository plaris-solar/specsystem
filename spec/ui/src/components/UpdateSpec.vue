<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">Update {{props.specRow['num']}}/{{props.specRow['ver']}} Spec</div>
            <q-btn icon="close" flat round dense data-cy="token-update-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Category" v-model.trim="cat" data-cy="cat-update-spec"/>
            <q-input label="Sub Category" v-model.trim="sub_cat" data-cy="sub_cat-update-spec"/>
            <q-input label="Title" v-model.trim="title" data-cy="title-update-spec"/>
            <q-input label="Keywords" v-model.trim="keywords" data-cy="title-update-spec" />
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveSpec()" data-cy="spec-update-update"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" v-close-popup data-cy="spec-update-cancel"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { defineProps, putData } from '@/utils.js'
import {ref, defineEmits, onMounted} from 'vue'

export default {
    name: 'UpdateSpecDialog',
}
</script>

<script setup>    
    const props = defineProps({
        specRow: Object,
        updateMode: Boolean,
    })

    const emit = defineEmits(['updateTable'])

    const cat = ref('')
    const sub_cat = ref('')
    const title = ref('')
    const keywords = ref('')

    async function saveSpec(){
        const body = {
            cat: cat.value + '/' + sub_cat.value,
            title: title.value,
            keywords: keywords.value,
            sigs:props.specRow['sigs'],
            files:props.specRow['files'],
            refs:props.specRow['refs'],
        }

        let res = await putData(`spec/${props.specRow['num']}/${props.specRow['ver']}`, body, 
            'Successfully updated spec ' + props.specRow['num'] + '/' + props.specRow['ver'])
        if (res.status < 300){
            emit('updateTable')
        }
    }

    onMounted(() => {
        let catArr = props.specRow['cat'].split('/')
        cat.value = catArr[0]
        sub_cat.value = catArr[1]
        title.value = props.specRow['title']
        keywords.value = props.specRow['keywords']
    })
</script>

<style scoped>
.filter-btn {
    width: 5em;
    margin-bottom: 2vh;
}

.dialog_window{
    max-width: 50vw;
    width: 50vw;
}

.spacer{
    width: 2vw;
}
</style>
