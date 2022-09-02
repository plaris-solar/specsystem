<template>
   <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h5">{{props.username}}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
            <q-input label="Delegates" v-model.trim="delegates" data-cy="user-detail-delegates" dense />
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
            <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveUser()" data-cy="spec-detail-update"/>
        </q-card-actions>
        <div class="q-pa-md">
            <q-table
                :rows="rows"
                :hide-bottom="true"
                dense
                data-cy="spec-table">
                <template v-slot:header>
                    <q-th style="text-align:left">
                        Specs Watched
                    </q-th>
                </template>
                <template v-slot:body="props">
                    <q-tr :props="props">
                        <q-td v-for="col in props.cols" :key="col.name" :props="props" style="text-align:left">
                            <span v-if="col.name === 'num'">
                                <router-link :to="'/ui-spec/'+props.row['num']+'/*'">
                                    {{props.row['num']}}
                                    </router-link>
                                &nbsp;
                                <q-btn round color="primary" 
                                        @click="clearWatch(props.row['num'].toString())"
                                        icon="visibility" size="xs"
                                        data-cy="clear-watch">
                                </q-btn>
                            </span>
                            <span v-else>{{props.row[col.name]}}</span>
                        </q-td>
                    </q-tr>
                </template>
                <template v-slot:bottom>
                    <q-btn @click="getTableData(page_num - 1)" :disable="page_num == 1" data-cy="data-prev-btn">
                        {{'<'}}
                    </q-btn>
                    <q-input input-class="text-right" 
                             v-model="page_num" 
                             class="page-input" 
                             @keydown.enter.prevent="getTableData(page_num)" 
                             data-cy="data-page-input"/>
                    <div class="num-pages" data-cy="data-num-pages">
                         &nbsp;/ {{num_pages}}
                    </div>
                    <q-btn @click="getTableData(page_num + 1)" :disable="page_num == num_pages" data-cy="data-next-btn">
                        {{'>'}}
                    </q-btn>
                </template>
            </q-table>
        </div>
    </q-card>
</template>

<script>
import { defineProps, deleteData, putData, retrieveData, } from '@/utils.js'
import {ref, onMounted} from 'vue'

export default {
    name: 'UserDetailPage',
}
</script>

<script setup>    
    const props = defineProps({
        username: String,
    })

    const delegates = ref('')
    const rows = ref([])

    async function saveUser(){
        const body = {
            delegates:delegates.value,
        }

        let res = await putData(`user/${props.username}`, body, 
            'Successfully updated user ' + props.username)
    }

    async function loadData() {
        let res = await retrieveData(`user/${props.username}`);
        delegates.value = res['delegates']
        rows.value = res['watches'].map(function(num){ return {num:num}})
    }

    onMounted(() => {
        loadData()
    })  
    
    async function clearWatch(num) {        
        deleteData(`user/watch/${props.username}/${num}`, '{}', `Deleted watch on: ${num} successfully.`).then((res) => {
            if (res.__resp_status < 300){
                loadData()
            }
        })
    }
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
