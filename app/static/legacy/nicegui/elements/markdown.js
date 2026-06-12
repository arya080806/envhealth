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
import { loadResource } from "../../static/utils/resources.js";
export default {
  template: `<div></div>`,
  mounted() {
    return __async(this, null, function* () {
      yield this.$nextTick();
      yield loadResource(window.path_prefix + `${this.dynamicResourcePath}/${this.resourceName}`);
      this.renderContent();
      if (this.useMermaid) {
        this.mermaid = (yield import("nicegui-mermaid")).mermaid;
        this.mermaid.initialize({ startOnLoad: false });
        this.renderMermaid();
      }
    });
  },
  data() {
    return {
      mermaid: null,
      diagrams: {},
      previousInnerHTML: null
    };
  },
  updated() {
    this.renderContent();
    this.renderMermaid();
  },
  methods: {
    renderContent() {
      if (this.innerHTML === this.previousInnerHTML) return;
      if (this.sanitize) {
        this.$el.setHTML(this.innerHTML);
      } else {
        this.$el.innerHTML = this.innerHTML;
      }
      this.previousInnerHTML = this.innerHTML;
    },
    renderMermaid() {
      if (!this.useMermaid || !this.mermaid) return;
      const usedKeys = /* @__PURE__ */ new Set();
      this.$el.querySelectorAll(".mermaid-pre").forEach((pre, i) => __async(this, null, function* () {
        var _a, _b;
        const key = pre.children[0].innerText + "\n" + i;
        usedKeys.add(key);
        if (!this.diagrams[key]) {
          try {
            this.diagrams[key] = yield this.mermaid.render(this.$el.id + "_mermaid_" + i, pre.children[0].innerText);
          } catch (error) {
            this.diagrams[key] = yield this.mermaid.render(this.$el.id + "_mermaid_" + i, "error");
            console.error(error);
          }
        }
        const svgElement = document.createElement("div");
        svgElement.classList.add("mermaid-svg");
        svgElement.innerHTML = this.diagrams[key].svg;
        (_b = (_a = this.diagrams[key]).bindFunctions) == null ? void 0 : _b.call(_a, svgElement);
        pre.querySelectorAll(".mermaid-svg").forEach((svg) => svg.remove());
        pre.appendChild(svgElement);
      }));
      for (const key in this.diagrams) {
        if (!usedKeys.has(key)) {
          delete this.diagrams[key];
        }
      }
    }
  },
  props: {
    innerHTML: String,
    dynamicResourcePath: String,
    resourceName: String,
    sanitize: Boolean,
    useMermaid: {
      required: false,
      default: false,
      type: Boolean
    }
  }
};
