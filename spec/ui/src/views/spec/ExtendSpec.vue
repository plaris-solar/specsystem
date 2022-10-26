<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">Extend Spec</div>
            <q-btn icon="close" flat round dense data-cy="spec-extend-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Reason" v-model.trim="comment" type="textarea" data-cy="spec-extend-comment"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Extend" color="primary" icon="more_time" @click="extendSunset()" data-cy="spec-extend-extend"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" icon="cancel" v-close-popup data-cy="spec-extend-cancel"/>
        </q-card-actions>

        <q-dialog v-model="rejectDisabled" no-esc-dismiss no-backdrop-dismiss>
            <q-card>
                <q-card-section align="center">
                    <h4>Updating sunset time. Please wait</h4>
                    <br/>
                    <p>Do not refresh the page.</p>
                </q-card-section>
            </q-card>
        </q-dialog>
    </q-card>
</template>

<script>
import { defineProps, postData, } from '@/utils.js'
import { defineEmits, ref, onMounted} from 'vue'

export default {
    name: 'ExtendSpecDialog',
}
</script>

<script setup>
    const props = defineProps({
        num: String,
        ver: String,
    })
    const comment = ref('')
    const emit = defineEmits(['updateSpec'])
    const rejectDisabled = ref(false)

    async function extendSunset(){
        rejectDisabled.value = true
        let res = await postData(`extend/${props.num}/${props.ver}`, 
            {'comment':comment.value}, 
            `Extended spec: ${props.num}/${props.ver} successfully.`)
        if (res.__resp_status < 300){
            emit('updateSpec')
        }
        rejectDisabled.value = false
    }

    onMounted(() => {
    })

</script>

<style scoped>
.dialog_window{
    max-width: 50vw;
    width: 50vw;
}

.spacer{
    width: 2vw;
}
</style>
