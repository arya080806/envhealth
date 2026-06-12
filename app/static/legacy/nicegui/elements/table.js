import { convertDynamicProperties } from "../../static/utils/dynamic_properties.js";
export default {
  template: '\n    <q-table ref="qRef" :columns="convertedColumns" @fullscreen="setFullscreenClass">\n      <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">\n        <slot :name="slot" v-bind="slotProps || {}" />\n      </template>\n    </q-table>\n  ',
  props: {
    columns: Array
  },
  computed: {
    convertedColumns() {
      this.columns.forEach((column) => convertDynamicProperties(column, false));
      return this.columns;
    }
  },
  methods: {
    setFullscreenClass(isFullscreen) {
      if (isFullscreen) {
        document.documentElement.classList.add("nicegui-table-fullscreen");
      } else {
        setTimeout(() => document.documentElement.classList.remove("nicegui-table-fullscreen"));
      }
    }
  },
  unmounted() {
    this.setFullscreenClass(false);
  }
};
