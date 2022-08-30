<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">{{props.createMode?'Create':'Update '}} Approval Matrix</div>
            <q-btn icon="close" flat round dense data-cy="token-create-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Document Type" v-model.trim="doc_type" data-cy="doc_type-create-ApprovalMatrix"/>
            <q-input label="Department" v-model.trim="department" data-cy="department-create-ApprovalMatrix"/>
            <q-input label="Required Signer Roles" v-model.trim="signRoles"  data-cy="signRoles-create-ApprovalMatrix"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveApprovalMatrix()" data-cy="ApprovalMatrix-create-create"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" v-close-popup data-cy="ApprovalMatrix-create-cancel"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { defineProps, postData, putData } from '@/utils.js'
import {ref, defineEmits, onMounted} from 'vue'

export default {
    name: 'CreateApprovalMatrixDialog',
}
</script>

<script setup>    
    const props = defineProps({
        ApprovalMatrixRow: Object,
        createMode: Boolean,
    })

    const emit = defineEmits(['updateTable'])

    const doc_type = ref('')
    const department = ref('')
    const id = ref('')
    const signRoles = ref('')

    async function saveApprovalMatrix(){
        const body = {
            doc_type: doc_type.value,
            department: department.value,
            signRoles: signRoles.value,
        }

        if (props.createMode) {
            let res = await postData('approvalmatrix/', body, 'Successfully created ApprovalMatrix ')
            if (res.__resp_status < 300){
                emit('updateTable')
            }
        }
        else {
            let res = await putData(`approvalmatrix/${id.value}`, body, 'Successfully updated ApprovalMatrix ')
            if (res.__resp_status < 300){
                emit('updateTable')
            }
        }
    }

    onMounted(() => {
        if (props.ApprovalMatrixRow['id'] !== undefined) {
            id.value = props.ApprovalMatrixRow['id']
            doc_type.value = props.ApprovalMatrixRow['doc_type']
            department.value = props.ApprovalMatrixRow['department']
            signRoles.value = props.ApprovalMatrixRow['signRoles']
        }
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
