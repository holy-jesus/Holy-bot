<script>
import { ClassicPreset as Classic, NodeEditor } from 'rete';
import { AreaPlugin } from 'rete-area-plugin';
import { ConnectionPlugin, Presets as ConnectionPresets } from 'rete-connection-plugin';
import { VuePlugin, Presets as VuePresets } from 'rete-vue-plugin';

const TriggerMessage = new Classic.Node("При сообщении")
TriggerMessage.addOutput()

async function createEditor(component) {
    const editor = new NodeEditor();
    const area = new AreaPlugin(component);
    const connection = new ConnectionPlugin();
    const vueRender = new VuePlugin();
    editor.use(area);
    area.use(vueRender);
    area.use(connection);
    connection.addPreset(ConnectionPresets.classic.setup());
    vueRender.addPreset(VuePresets.classic.setup());
}

export default {
    mounted() {
        createEditor(this.$refs.rete)
    }
}

</script>

<template>
    <div class="rete w-screen h-screen" ref="rete"></div>
</template>