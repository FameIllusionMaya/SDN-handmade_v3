<template>
  <div class="container">
    <div class="col-lg-4">
      <h3><b-badge variant="warning" size="lg">Initialization</b-badge></h3>
      <b-form @submit.prevent="initSystem">
        <b-form-group label="Controller IP">
          <b-form-input v-model="controller_ip" type="text" placeholder="Enter Controller IP"/>
        </b-form-group>
    </b-form>
    <b-button class="init_button" variant="success" v-on:click="setNetflow">Init Netflow</b-button>
    <b-button class="init_button" variant="success" v-on:click="setSNMP">Init SNMP</b-button>
    </div>
  </div>
</template>

<script lang="ts">

import { defineComponent, onMounted, reactive, watchEffect, ref, watch } from "vue";
import client from "../apiclient";
import Swal from 'sweetalert2';

export default {
  setup(){
    // management_ip service
    const controller_ip = ref<string>('')
    async function initSystem(){
      console.log('netflow init')
      setNetflow()
      console.log('snmp init')
      setSNMP()
    }
    async function setNetflow(){
      const {
        data: { success, message }
      } = await client.initNetflow({service:'netflow', management_ip:controller_ip})
      if(success){
        Swal.fire({title:"Init Netflow Success", icon:"success"})
      } else{
        Swal.fire({title:"Init Netflow Fail", icon:"error", text:message})
      }
    }
    
    async function setSNMP(){
      const {
        data: { success, message }
      } = await client.initNetflow({service:'snmp'})
      if(success){
        Swal.fire({title:"Init SNMP Success", icon:"success"})
      } else{
        Swal.fire({title:"Init SNMP Fail", icon:"error", text:message})
      }
    }

    return {controller_ip, initSystem, setNetflow, setSNMP}
  }
}
</script>
<style>
.init_button{
  margin:10px;
}
</style>