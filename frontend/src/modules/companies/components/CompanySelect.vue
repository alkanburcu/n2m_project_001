<script setup>

import{
    computed,
    onBeforeUnmount,
    ref,
    watch,
}from 'vue'

import{
    IconBuilding,
    IconChevronDown,
    IconPlus,
    IconSearch,
}from '@tabler/icons-vue'

import { useCompanyStore } from '../store/companyStore';

const props = defineProps({
  modelValue: {
    type: String,
    default: null,
  },

  initialCompany: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits([
    'update:modelValue',
    'add-company',
])

const companyStore = useCompanyStore()

const isOpen = ref(false)
const searchInput = ref('')
const dropdownRef = ref(null)

let searchTimer = null

const selectedCompany = computed(() => {
  const company =
    companyStore.companies.find(
      (item) => {
        return item.id === props.modelValue
      },
    )

  if (company) {
    return company
  }

  if (
    props.initialCompany?.id
    === props.modelValue
  ) {
    return props.initialCompany
  }

  return null
})

const openDropdown = async () => {
  isOpen.value = true

  if (
    companyStore.companies.length === 0
  ) {
    await companyStore.fetchCompanies()
  }
}


const closeDropdown = () => {
  isOpen.value = false
}


const toggleDropdown = async () => {
  if (isOpen.value) {
    closeDropdown()
    return
  }

  await openDropdown()
}


const selectCompany = (company) => {
  emit(
    'update:modelValue',
    company.id,
  )

  closeDropdown()
}


const clearCompany = () => {
  emit(
    'update:modelValue',
    null,
  )

  closeDropdown()
}


const handleScroll = async (event) => {
  const element = event.currentTarget

  const distanceFromBottom =
    element.scrollHeight
    - element.scrollTop
    - element.clientHeight

  if (
    distanceFromBottom < 40
    && companyStore.hasMore
    && !companyStore.isLoadingMore
  ) {
    await companyStore.loadMore()
  }
}


const handleClickOutside = (event) => {
  if (
    dropdownRef.value
    && !dropdownRef.value.contains(
      event.target,
    )
  ) {
    closeDropdown()
  }
}


watch(
  searchInput,
  (value) => {
    clearTimeout(searchTimer)

    searchTimer = setTimeout(
      async () => {
        await companyStore.fetchCompanies({
          search: value.trim(),
        })
      },
      300,
    )
  },
)


document.addEventListener(
  'click',
  handleClickOutside,
)


onBeforeUnmount(() => {
  clearTimeout(searchTimer)

  document.removeEventListener(
    'click',
    handleClickOutside,
  )
})
</script>

<template>
  <div
    ref="dropdownRef"
    class="company-select"
  >
    <button
      type="button"
      class="company-select__trigger"
      :aria-expanded="isOpen"
      @click="toggleDropdown"
    >
      <span
        class="company-select__value"
      >
        <IconBuilding
          :size="17"
          :stroke-width="1.8"
        />

        {{
          selectedCompany?.name
          || 'Select a company'
        }}
      </span>

      <IconChevronDown
        :size="16"
        :stroke-width="1.8"
        class="company-select__chevron"
        :class="{
          'company-select__chevron--open':
            isOpen,
        }"
      />
    </button>

    <div
      v-if="isOpen"
      class="company-select__dropdown"
    >
      <div
        class="company-select__search"
      >
        <IconSearch
          :size="16"
          :stroke-width="1.8"
        />

        <input
          v-model="searchInput"
          type="text"
          placeholder="Search companies..."
          @click.stop
        >
      </div>

      <div
        class="company-select__options"
        @scroll="handleScroll"
      >
        <button
          type="button"
          class="
            company-select__option
            company-select__option--empty
          "
          @click="clearCompany"
        >
          No company
        </button>

        <button
          v-for="company in companyStore.companies"
          :key="company.id"
          type="button"
          class="company-select__option"
          :class="{
            'company-select__option--selected':
              company.id === modelValue,
          }"
          @click="selectCompany(company)"
        >
          <span>
            {{ company.name }}
          </span>

          <small v-if="company.city">
            {{ company.city }}
          </small>
        </button>

        <div
          v-if="companyStore.isLoading"
          class="company-select__state"
        >
          Loading companies...
        </div>

        <div
          v-else-if="
            !companyStore.isLoading
            && companyStore.companies.length === 0
          "
          class="company-select__state"
        >
          No companies found.
        </div>

        <div
          v-if="companyStore.isLoadingMore"
          class="company-select__state"
        >
          Loading more...
        </div>
      </div>

      <button
        type="button"
        class="company-select__add"
        @click="
          emit('add-company')
        "
      >
        <IconPlus
          :size="17"
          :stroke-width="1.9"
        />

        Add company
      </button>
    </div>
  </div>
</template>

<style scoped>
.company-select {
  position: relative;
}

.company-select__trigger {
  width: 100%;
  min-height: 40px;

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;

  padding: 0 11px;

  color: var(--color-title);

  font: inherit;
  font-size: 13.5px;

  background: #ffffff;

  border: 1px solid var(--color-border);
  border-radius: 8px;

  cursor: pointer;

  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.company-select__trigger:hover,
.company-select__trigger[aria-expanded='true'] {
  border-color:
    rgba(82, 63, 158, 0.42);

  box-shadow:
    0 0 0 3px
    rgba(82, 63, 158, 0.07);
}

.company-select__value {
  min-width: 0;

  display: flex;
  align-items: center;
  gap: 8px;

  overflow: hidden;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.company-select__chevron {
  flex-shrink: 0;

  transition:
    transform 0.18s ease;
}

.company-select__chevron--open {
  transform: rotate(180deg);
}

.company-select__dropdown {
  position: absolute;
  top: calc(100% + 7px);
  right: 0;
  left: 0;

  z-index: 30;

  overflow: hidden;

  background: #ffffff;

  border: 1px solid var(--color-border);
  border-radius: 10px;

  box-shadow:
    0 12px 28px
    rgba(31, 36, 49, 0.11);
}

.company-select__search {
  display: flex;
  align-items: center;
  gap: 8px;

  padding: 9px 10px;

  border-bottom:
    1px solid var(--color-border);
}

.company-select__search input {
  width: 100%;

  padding: 0;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;

  background: transparent;

  border: 0;
  outline: 0;
}

.company-select__options {
  max-height: 230px;

  overflow-y: auto;

  padding: 5px;
}

.company-select__option {
  width: 100%;

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;

  padding: 9px 10px;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;

  text-align: left;

  background: transparent;

  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.company-select__option:hover {
  background:
    rgba(82, 63, 158, 0.055);
}

.company-select__option--selected {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.08);
}

.company-select__option--empty {
  color: var(--color-subtitle);
}

.company-select__option small {
  color: var(--color-subtitle);

  font-size: 11px;
}

.company-select__state {
  padding: 12px 10px;

  color: var(--color-subtitle);

  font-size: 12px;

  text-align: center;
}

.company-select__add {
  width: 100%;

  display: flex;
  align-items: center;
  gap: 8px;

  padding: 10px 12px;

  color: var(--color-primary);

  font: inherit;
  font-size: 12.5px;
  font-weight: 600;

  text-align: left;

  background:
    rgba(82, 63, 158, 0.035);

  border: 0;
  border-top:
    1px solid var(--color-border);

  cursor: pointer;
}

.company-select__add:hover {
  background:
    rgba(82, 63, 158, 0.08);
}
</style>