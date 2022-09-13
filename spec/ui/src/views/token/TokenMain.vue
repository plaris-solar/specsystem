<template>
    <q-page>
        <div class="q-pa-md row">
        
            <div class="row manage-tools">
                <div class="text-right upload-btn">  
                    <q-btn color="green" size='large' :disable="!isAdmin" @click="new_tok = true" data-cy="token-create-btn">
                        <div class="text-center">
                            New Token
                        </div>
                    </q-btn>
                </div>

                <div class="text-right upload-btn">  
                    <q-btn color="negative" size='large' @click="deleteToken()" :disable="!isAdmin" data-cy="token-delete-btn">
                        <div class="text-center">
                            Delete Token
                        </div>
                    </q-btn>
                </div>
            </div>
            <q-table
            title="Token Management"
            :rows="rows"
            :columns="columns"
            selection="single"
            row-key="user"
            :separator="'cell'"
            v-model:selected="selected"
            data-cy="token-table">
            <template v-slot:body="props">
                <q-tr :props="props">
                    <q-td class="text-center">
                        <q-checkbox v-model="props.selected" color="primary" />
                    </q-td>
                    <q-td
                        v-for="col in props.cols"
                        :key="col.name"
                        :props="props"
                        class="cell"
                    >
                        {{ col.value }}
                    </q-td>
                </q-tr>
                <q-tr v-show="props.selected" :props="props">
                    <q-td colspan="100%">
                        <div class="text-left">Token Value: {{ tok_vals[props.row.user] }}.</div>
                    </q-td>
                </q-tr>
            </template>
            </q-table>
        </div>
    </q-page>
    <q-dialog v-model="new_tok">
        <create-token-dialog @newToken="tokenCreated()"/>
    </q-dialog >
</template>

<script>
    import {
        retrieveData,
        showNotif,
        deleteData,
        postData
    } from '@/utils.js';

    import { ref, computed, onMounted } from 'vue';
    import { useStore } from 'vuex'
    import CreateTokenDialog from '@/views/token/CreateToken.vue'

    export default {
        name: 'TokenPage',
        components: {
            CreateTokenDialog,
        }
    }
    const columns = [
            { name: 'user', align: 'center', label: 'User', field: 'user', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'created', align: 'center', label: 'Created', field: 'created', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'exp_date', align: 'center', label: 'Expires in', field: 'expires_in', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'expired', align: 'center', label: 'Expired', field: 'expired', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'admin', align: 'center', label: 'Admin', field: 'admin', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'read_all', align: 'center', label: 'Read All', field: 'read_all', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'active', align: 'center', label: 'Active', field: 'active', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
        ]
</script>

<script setup>

    const store = useStore();
    const isAdmin = ref(computed(() => store.getters.isAdmin))
    const rows = ref([])
    const new_tok = ref(false)
    const selected = ref([])
    const tok_vals = ref({})

    onMounted(() => {
        getTokenList();
    })

    async function tokenCreated(){
        new_tok.value = false;
        getTokenList();
    }

    async function getTokenVal(user){
        if ((typeof user !== 'undefined') && user){
            let res = await postData(`auth/token/${user}`, {}, null)
            return res['Authorization']
        }
    }

    async function getTokenList(){
        rows.value = await retrieveData('auth/token')

        tok_vals.value = {}
        for (const row of rows.value){
            let tok = await getTokenVal(row['user'])
            tok_vals.value[row['user']] = tok
        }
    }

    async function deleteToken(){
        if (selected.value.length < 1) {
            showNotif('No selected rows to delete.', 'grey')
            return
        }
        let user = selected.value[0]['user']
        await deleteData(`auth/token/${user}`, {}, `Successfully deleted token for ${user}`)
        getTokenList()
    }

</script>

<style scoped>
li {
    font-size: 20px;
}

.tab {
    font-size: large;
}

.page-col {
    font-weight: bold;
}

.hyperlink {
    color: blue;
}

.upload-btn {
    padding-left: 5vh;
}

.manage-tools {
    margin-bottom:2em;
    margin-top: 5em;
}

.schema-col {
    text-align: left; 
    width: 15em;
}

.cell{
    font-size: 1em
}

</style>