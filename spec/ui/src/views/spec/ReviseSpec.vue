<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">Revise Spec</div>
            <q-btn icon="close" flat round dense data-cy="spec-create-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Reason" v-model.trim="reason" type="textarea" data-cy="spec-revise-reason"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Revise" color="primary" icon="save" @click="reviseSpec()" data-cy="spec-revise-revise"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" icon="cancel" v-close-popup data-cy="spec-revise-cancel"/>
        </q-card-actions>

        <q-dialog v-model="reviseDisabled" no-esc-dismiss no-backdrop-dismiss>
            <q-card>
                <q-card-section align="center">
                    <h4>Creating new spec. Please wait</h4>
                    <p>This may take a minute while the Spec and Jira stories are created.</p>
                    <br/>
                    <p>Do not refresh the page.</p>
                </q-card-section>
            </q-card>
        </q-dialog>
    </q-card>
</template>

<script>
import { defineProps, postData, showNotif, } from '@/utils.js'
import { ref, onMounted} from 'vue'
import { useRouter, } from 'vue-router'

export default {
    name: 'ReviseSpecDialog',
}
</script>

<script setup>
    const props = defineProps({
        num: String,
        ver: String,
    })
    const reason = ref('')
    const reviseDisabled = ref(false)
    const router=useRouter();

    async function reviseSpec(){
        reviseDisabled.value = true
        let res = await postData(`spec/${props.num}/${props.ver}`, {'reason':reason.value}, null)
        if (res.__resp_status < 300) {
            showNotif(`Spec created: ${res.num}/${res.ver}`, 'green')
            router.push({name:"Spec Detail", params:{num:res.num, ver:res.ver}})
        }
        reviseDisabled.value = false
    }


    onMounted(() => {
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
