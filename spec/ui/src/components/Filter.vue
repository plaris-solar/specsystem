<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="col-4"/>
            <div class="text-h4 col-4 text-center">Advanced Filter</div>
            <div class="col-4 text-right">             
                <q-btn icon="close" flat round dense v-close-popup /> 
            </div>
        </q-card-section>
        <q-card-section v-for="n in [0,1,2]" :key="n" class="q-pt-none">
            <div class="row justify-center col-6 q-gutter-x-md filter-row">
                <q-select outlined 
                    :options="display_filters[n]"
                    v-model= filters[n]
                    use-input
                    input-debounce="0"
                    color="blue"
                    label="Select filter"
                    class="q-pa-sm text-h6 filter-select-width"
                    clearable
                    @clear="clearFilter(n)" 
                    @filter="(val, update) => filterFn(val, update, n)"
                    :data-cy="genCy('filter-select', n)">
                </q-select>
                <div class="spacer"/>
                <q-input class="q-pa-sm text-h6" 
                                v-model="filter_vals[n]"
                                outlined
                                label="Filter value"
                                :data-cy="genCy('filter-input', n)"/>
            </div>
        </q-card-section>

        <q-card-section>
            <div class="row justify-center col-6 q-gutter-x-md date-select" >
                <q-input filled v-model="from_date" label="From date..." :rules="['date']" data-cy="filter-date-lower-input">
                    <template v-slot:append>
                        <q-icon name="event" class="cursor-pointer">
                            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                                <q-date v-model="from_date" :options="lowerDateBound" data-cy="filter-date-lower-select">
                                <div class="row items-center justify-end">
                                    <q-btn v-close-popup label="Close" color="primary" flat data-cy="filter-date-lower-close"/>
                                </div>
                                </q-date>
                            </q-popup-proxy>
                        </q-icon>
                    </template>
                </q-input>
                <div class="spacer-large"/>
                <q-input filled mask="date" v-model="to_date" label="To date..." data-cy="filter-date-upper-input">
                    <template v-slot:append>
                        <q-icon name="event" class="cursor-pointer">
                            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                                <q-date v-model="to_date" :options="upperDateBound" data-cy="filter-date-upper-select">
                                    <div class="row items-center justify-end">
                                        <q-btn v-close-popup label="Close" color="primary" flat data-cy="filter-date-upper-close"/>
                                    </div>
                                </q-date>
                            </q-popup-proxy>
                        </q-icon>
                    </template>
                </q-input>
            </div>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Apply" 
                 color="primary" 
                 size="lg" 
                 class="filter-btn" 
                 @click="applyFilter()" 
                 data-cy="filter-apply-btn" 
                 v-close-popup />
          <div class="spacer"/>
          <q-btn label="Clear" color="cyan" size="lg" class="filter-btn" @click="clearFilters()" data-cy="filter-clear-btn"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" data-cy="filter-cancel-btn" v-close-popup />
        </q-card-actions>
    </q-card>
</template>

<script>
import {ref, onMounted, defineProps, defineEmits} from 'vue'
import { genCy } from '@/utils'

export default {
    name: 'FilterDialogueWindow',
}
</script>

<script setup>

    const from_date = ref(null)
    const to_date = ref(null)

    const filters = ref([null, null, null])
    const filter_vals = ref([null, null, null])
    const display_filters = ref([null, null, null])
    

    const props = defineProps({
        col_names: Array,
        advanced_filter_dict: Object
    })

    const emit = defineEmits(['newFilterSlug'])

    onMounted(() => {
        getExistingFilters(props.advanced_filter_dict)
        display_filters.value = [props.col_names, props.col_names, props.col_names]
    })

    async function clearFilter(idx){
        filters.value[idx] = null
        filter_vals.value[idx] = null
    }

    async function clearFilters(){
        filters.value = [null, null, null]
        filter_vals.value = [null, null, null]
        to_date.value = null;
        from_date.value = null;
    }

    function getExistingFilters(filter_dict){
        let filter_idx = 0
        if ('lower_date' in filter_dict){
            from_date.value = filter_dict['lower_date']
            delete filter_dict['lower_date']
        }
        if ('upper_date' in filter_dict){
            to_date.value = filter_dict['upper_date']
            delete filter_dict['upper_date']
        }
        for (let [key, value] of Object.entries(filter_dict)){
            filters.value[filter_idx] = key
            filter_vals.value[filter_idx] = value
            filter_idx++
        }
    }

    function upperDateBound(date){
        if (from_date.value){
            return date >= from_date.value
        }
        return true
    }

    function lowerDateBound(date){
        if (to_date.value){
            return date <= to_date.value
        }
        return true
    }

    async function applyFilter(){
        var filter_dict = {}
        for (let i = 0; i < 3; i++) {
            if (filters.value[i]){
                filter_dict[filters.value[i]] = filter_vals.value[i]
            }
        }
        if (from_date.value){
            filter_dict['lower_date'] = from_date.value
        }
        if (to_date.value){
            filter_dict['upper_date'] = to_date.value
        }
        emit('newFilterSlug', filter_dict)
    }

    function filterFn (val, update, select_idx) {
        if (val === ''){
            update(() => {
                display_filters.value[select_idx] = props.col_names;
            })
        return;
        }
        update(() => {
            display_filters.value[select_idx] = props.col_names
            const needle = val.toUpperCase()
            display_filters.value[select_idx] = display_filters.value[select_idx].filter(v => v.toUpperCase().indexOf(needle) > -1)
        })
    }

</script>

<style scoped>
.filter-btn {
    width: 5em;
    margin-bottom: 2vh;
}

.dialog-window{
    max-width: 50vw;
    width: 50vw;
}

.spacer{
    width: 2vw;
}

.filter-row{
     margin-top: 2vh;
}

.filter-select-width{
    width: 20vw
}

.date-select{
    margin-top: 2vh
}

.spacer-large{
    width: 4em;
}
</style>
