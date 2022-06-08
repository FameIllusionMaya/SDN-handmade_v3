<template>
  <div class="container">
    <div class="row">
      <div class="col-6" >
        <h3><b-badge variant="primary" size="lg">Devices List</b-badge></h3>
        <div id="Devices_list" class="d-grid gap-2">
          <b-button class="device_button" size="sm" block :variant='selected_device.index===index?"outline-success":"outline-primary"'
          v-for="(device, index) in device_list" v-bind:key="index" v-on:click="toggle_mode(index)">
            <h4>{{device.name}}</h4>
            <h6>{{"Management IP: " + device.management_ip}}</h6>
            <b-badge pill :variant='device.is_ssh_connect?"success":"danger"'>SSH</b-badge>
            <b-badge pill :variant='device.is_snmp_connect?"success":"danger"'>SNMP</b-badge>
          </b-button>
          <!-- <b-card :header='"Management IP: " + device.management_ip' header-bg-variant="light"
          v-for="(device, index) in device_list" v-bind:key="index" v-on:click="toggle_mode(index)"
          :title=device.name>
            <b-badge pill :variant='device.is_ssh_connect?"success":"danger"'>SSH</b-badge>
            <b-badge pill :variant='device.is_snmp_connect?"success":"danger"'>SNMP</b-badge>
          </b-card> -->
        </div>
      </div>
      <div class="col-6">
        <h3>
          <b-badge :variant='patch_device_enable?"success":"warning"' size="lg">
            {{patch_device_enable?selected_device.name:"New Device Info"}}
          </b-badge>
        </h3>
          <b-form @submit.prevent="formSubmit" id="DeviceForm">
            
            <b-form-group label="Management IP">
              <b-form-input size="sm" v-model="device_data.management_ip" placeholder="Enter Management IP" required/>
            </b-form-group>
            <b-form-group label="System Type">
              <b-form-select size="sm" v-model="device_data.type" :options="
              [
              {value: null, text: 'Select System Type'},
              {value: 'cisco_ios', text:'cisco_ios'},
              ]
              " required/>
            </b-form-group>
            <b-form-group label="SSH Username">
              <b-form-input size="sm" v-model="device_data.ssh_info.username" placeholder="Enter SSH Username" required/>
            </b-form-group>
            <b-form-group label="SSH Password">
              <b-form-input size="sm" v-model="device_data.ssh_info.password" placeholder="Enter SSH Password" required/>
            </b-form-group>
            <b-form-group label="SSH Secret">
              <b-form-input size="sm" v-model="device_data.ssh_info.secret" placeholder="Enter SSH Secret" required/>
            </b-form-group>
            <b-form-group label="SSH Port">
              <b-form-input size="sm" v-model="device_data.ssh_info.port" placeholder="Enter SSH Port" required/>
            </b-form-group>
            <b-form-group label="SNMP Version">
              <b-form-select size="sm" v-model="device_data.snmp_info.version" :options="
              [
              {value: null, text: 'Select SNMP Version'},
              {value: '2c', text:'2c'}
              ]
              " required/>
            </b-form-group>
            <b-form-group label="SNMP Community String">
              <b-form-input size="sm" v-model="device_data.snmp_info.community" placeholder="Enter SNMP Community String" required/>
            </b-form-group>
            <b-form-group label="SNMP Port">
              <b-form-input size="sm" v-model="device_data.snmp_info.port" placeholder="Enter SNMP Port" required/>
            </b-form-group>
            <b-button :variant='patch_device_enable?"success":"warning"' type="submit">
              {{ patch_device_enable?"Patch Device":"Add Device" }}
            </b-button>
            <b-button variant="danger" v-show="patch_device_enable" v-on:click="removeDevice()">
              Remove {{selected_device.name}}
            </b-button>
          </b-form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, watchEffect, ref, watch } from "vue";
import client from "../apiclient";
import Swal from 'sweetalert2'


export default {
  setup(){
    const patch_device_enable = ref<boolean>(false)
    const device_data = reactive({
          _id:'',
          management_ip:'',
          type:'',
          ssh_info:{
            username:'',
            password:'',
            secret:'',
            port:'22'
          },
          snmp_info:{
            community:'',
            port:'161',
            version:'',
          }
        })
    const selected_device = reactive({serial:'', _id:{$oid:''}, index:-1})
    const device_list = reactive({})
    const overlay = ref<boolean>(false)

    async function toggle_mode(index){
      if(selected_device.serial===device_list[index].serial){
        patch_device_enable.value = false
        Object.assign(device_data, {
          management_ip:'',
          type:'',
          ssh_info:{
            username:'',
            password:'',
            secret:'',
            port:''
          },
          snmp_info:{
            community:'',
            port:'',
            version:'',
          }
        })
        Object.assign(selected_device, {
          index:-1,
          serial:'',
          management_ip:'',
          type:'',
          ssh_info:{
            username:'',
            password:'',
            secret:'',
            port:''
          },
          snmp_info:{
            community:'',
            port:'',
            version:'',
          }
        })
        console.log('dup')
        // console.log(selected_device)
      }
      else{
        patch_device_enable.value = true
        Object.assign(selected_device, device_list[index])
        selected_device.index = index
        Object.assign(device_data, {
          _id: device_list[index]._id.$oid,
          management_ip: device_list[index].management_ip,
          type: device_list[index].type,
          ssh_info:{
            username: device_list[index].ssh_info.username,
            password: device_list[index].ssh_info.password,
            secret: device_list[index].ssh_info.secret,
            port: device_list[index].ssh_info.port
          },
          snmp_info:{
            community: device_list[index].snmp_info.community,
            port: device_list[index].snmp_info.port,
            version: device_list[index].snmp_info.version ,
          }
        })
      }
      console.log('toggle ' + index)
    }

    async function addDevice(){
      console.log('add')
      overlay.value = true
      const {
        data: { success }
      } = await client.postDevice(
        {
          management_ip: device_data.management_ip, 
          type: device_data.type,
          ssh_info:{
            username: device_data.ssh_info.username,
            password: device_data.ssh_info.password,
            secret: device_data.ssh_info.secret,
            port: device_data.ssh_info.port===''?-1:parseInt(device_data.ssh_info.port, 10),
          },
          snmp_info:{
            community: device_data.snmp_info.community,
            port: device_data.snmp_info.port===''?-1:parseInt(device_data.snmp_info.port, 10),
            version: device_data.snmp_info.version
          }
        }
      );
      if(success){
        Swal.fire({title:"Device was added", icon:"success", confirmButtonText:"Okay"})
      }
      else{
        Swal.fire({title:"Error during add process", icon:"error", confirmButtonText:"Okay"})
      }
      overlay.value = false

    }

    async function patchDevice(){
      console.log('patch')
      overlay.value = true

      const {
        data: { success }
      } = await client.patchDevice(
        {
          _id: device_data._id,
          management_ip: device_data.management_ip, 
          type: device_data.type,
          ssh_info:{
            username: device_data.ssh_info.username,
            password: device_data.ssh_info.password,
            secret: device_data.ssh_info.secret,
            port: device_data.ssh_info.port===''?-1:parseInt(device_data.ssh_info.port, 10),
          },
          snmp_info:{
            community: device_data.snmp_info.community,
            port: device_data.snmp_info.port===''?-1:parseInt(device_data.snmp_info.port, 10),
            version: device_data.snmp_info.version
          }
        }, device_data._id
      );
      if(success){
        Swal.fire({title:"Device was patched", icon:"success", confirmButtonText:"Okay"})
      }
      else{
        Swal.fire({title:"Error during patch process", icon:"error", confirmButtonText:"Okay"})
      }
      overlay.value = false

    }

    async function removeDevice(){
      console.log({device_id:selected_device._id.$oid})
      overlay.value = true
      const {
        data: { success }
      } = await client.deleteDevice(selected_device._id.$oid)
      if(success){
        Swal.fire({title:'Device was removed', icon:"success", confirmButtonText:"Okay"})
      }else{
        Swal.fire({title:"Error during remove process", icon:"error", confirmButtonText:"Okay"})
      }
      delete device_list[selected_device.index]
      overlay.value = false

    }
    async function formSubmit(){
      if(patch_device_enable.value){
        patchDevice()
      }
      else{
        addDevice()
      }
      fetchDevice()
    }

    async function fetchDevice(){
      console.log('fetch')
      const {
        data: { devices }
      } = await client.getAllDevices()
      console.log(device_list)
      console.log('---')
      console.log(devices)
      Object.assign(device_list, devices)
      // console.log(devices)
    }
    onMounted(() => {
      fetchDevice();
      setInterval(()=>fetchDevice(), 5000);
    });

  
    return {device_data, device_list, patch_device_enable, selected_device, toggle_mode, formSubmit, removeDevice}
  }

}
</script>
<style>
#Devices_list{
  height: 80vh;
  overflow: scroll;
}

#DeviceForm{
  height: 80vh;
  overflow: scroll;
}
.device_button{

}
</style>

