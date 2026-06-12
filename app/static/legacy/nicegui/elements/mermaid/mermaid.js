var __async = (__this, __arguments, generator) => {
  return new Promise((resolve, reject) => {
    var fulfilled = (value) => {
      try {
        step(generator.next(value));
      } catch (e) {
        reject(e);
      }
    };
    var rejected = (value) => {
      try {
        step(generator.throw(value));
      } catch (e) {
        reject(e);
      }
    };
    var step = (x) => x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected);
    step((generator = generator.apply(__this, __arguments)).next());
  });
};
import { mermaid } from "nicegui-mermaid";
let is_running = false;
const queue = [];
export default {
  template: `<div></div>`,
  data: () => ({
    last_content: ""
  }),
  mounted() {
    this.initialize();
    this.update(this.content);
  },
  methods: {
    initialize() {
      try {
        mermaid.initialize(this.config || {});
      } catch (error) {
        console.error(error);
        this.$emit("error", error);
      }
    },
    update(content) {
      return __async(this, null, function* () {
        if (this.last_content === content) return;
        this.last_content = content;
        queue.push({ element: this.$el, content, clickable: this.clickable });
        if (is_running) return;
        is_running = true;
        while (queue.length) {
          const { element, content: content2, clickable } = queue.shift();
          try {
            const { svg, bindFunctions } = yield mermaid.render(element.id + "_mermaid", content2);
            element.innerHTML = svg;
            bindFunctions == null ? void 0 : bindFunctions(element);
            if (clickable) {
              element.querySelectorAll("g.node").forEach((node) => {
                node.style.cursor = "pointer";
                node.addEventListener("click", () => getElement(element).$emit("node_click", node.id));
              });
            }
          } catch (error) {
            const { svg, bindFunctions } = yield mermaid.render(element.id + "_mermaid", "error");
            element.innerHTML = svg;
            bindFunctions == null ? void 0 : bindFunctions(element);
            const mermaidErrorFormat = { str: error.message, message: error.message, hash: error.name, error };
            console.error(mermaidErrorFormat);
            getElement(element).$emit("error", mermaidErrorFormat);
          }
        }
        is_running = false;
      });
    }
  },
  props: {
    config: Object,
    content: String,
    clickable: Boolean
  }
};
