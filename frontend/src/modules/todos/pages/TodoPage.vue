<script setup>
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue'

import { useRoute } from 'vue-router'

import {
  IconPlus,
  IconTrash,
} from '@tabler/icons-vue'

import { useAuthStore } from '@/modules/auth/store/authStore'
import todoService from '../services/todoService'

const route = useRoute()
const authStore = useAuthStore()

const todos = ref([])

const todoTitles = ref({})
const newTodoTitle = ref('')

const selectedTodoId = ref(null)

const newTodoInput = ref(null)

const isLoading = ref(false)
const isCreating = ref(false)

const updatingTodoIds = ref([])
const deletingTodoIds = ref([])

const errorMessage = ref('')

const replaceTodo = (updatedTodo) => {
  const index = todos.value.findIndex(
    (todo) => todo.id === updatedTodo.id,
  )

  if (index !== -1) {
    todos.value[index] = updatedTodo
  }

  todoTitles.value[updatedTodo.id] =
    updatedTodo.title
}

const fetchTodos = async (userId) => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response =
      await todoService.getTodosByUser(userId)

    todos.value = response.data

    todoTitles.value = Object.fromEntries(
      response.data.map((todo) => [
        todo.id,
        todo.title,
      ]),
    )
  } catch (error) {
    console.error(
      'Failed to fetch todos:',
      error,
    )

    errorMessage.value =
      'Todos could not be loaded.'
  } finally {
    isLoading.value = false
  }
}

/* -------------------------
   CREATE
------------------------- */

const createTodo = async () => {
  const title = newTodoTitle.value.trim()

  if (
    !title
    || isCreating.value
    || !authStore.can('todos.create')
  ) {
    return
  }

  isCreating.value = true
  errorMessage.value = ''

  try {
    const response =
      await todoService.createTodo({
        user: route.params.id,
        title,
      })

    todos.value.push(response.data)

    todoTitles.value[response.data.id] =
      response.data.title

    newTodoTitle.value = ''

    await nextTick()

    newTodoInput.value?.focus()
  } catch (error) {
    console.error(
      'Failed to create todo:',
      error,
    )

    errorMessage.value =
      'Todo could not be created.'
  } finally {
    isCreating.value = false
  }
}

/* -------------------------
   TITLE UPDATE
------------------------- */

const saveTodoTitle = async (todo) => {
  if (!authStore.can('todos.update')) {
    return
  }

  const title =
    todoTitles.value[todo.id]?.trim() ?? ''

  if (!title) {
    todoTitles.value[todo.id] =
      todo.title

    return
  }

  if (
    title === todo.title
    || updatingTodoIds.value.includes(todo.id)
  ) {
    return
  }

  updatingTodoIds.value.push(todo.id)
  errorMessage.value = ''

  try {
    const response =
      await todoService.updateTodo(
        todo.id,
        {
          title,
        },
      )

    replaceTodo(response.data)
  } catch (error) {
    console.error(
      'Failed to update todo title:',
      error,
    )

    todoTitles.value[todo.id] =
      todo.title

    errorMessage.value =
      'Todo could not be updated.'
  } finally {
    updatingTodoIds.value =
      updatingTodoIds.value.filter(
        (id) => id !== todo.id,
      )
  }
}

const resetTodoTitle = (todo) => {
  todoTitles.value[todo.id] =
    todo.title
}

/* -------------------------
   COMPLETED
------------------------- */

const toggleTodo = async (todo) => {
  if (
    updatingTodoIds.value.includes(todo.id)
    || !authStore.can('todos.update')
  ) {
    return
  }

  updatingTodoIds.value.push(todo.id)

  errorMessage.value = ''

  try {
    const response =
      await todoService.updateTodo(
        todo.id,
        {
          completed: !todo.completed,
        },
      )

    replaceTodo(response.data)
  } catch (error) {
    console.error(
      'Failed to update todo:',
      error,
    )

    errorMessage.value =
      'Todo could not be updated.'
  } finally {
    updatingTodoIds.value =
      updatingTodoIds.value.filter(
        (id) => id !== todo.id,
      )
  }
}

/* -------------------------
   DELETE
------------------------- */

const deleteTodo = async (todoId) => {
  if (
    deletingTodoIds.value.includes(todoId)
    || !authStore.can('todos.delete')
  ) {
    return false
  }

  deletingTodoIds.value.push(todoId)

  errorMessage.value = ''

  try {
    await todoService.deleteTodo(todoId)

    todos.value =
      todos.value.filter(
        (todo) => todo.id !== todoId,
      )

    delete todoTitles.value[todoId]

    if (selectedTodoId.value === todoId) {
      selectedTodoId.value = null
    }

    return true
  } catch (error) {
    console.error(
      'Failed to delete todo:',
      error,
    )

    errorMessage.value =
      'Todo could not be deleted.'

    return false
  } finally {
    deletingTodoIds.value =
      deletingTodoIds.value.filter(
        (id) => id !== todoId,
      )
  }
}

/* -------------------------
   KEYBOARD
------------------------- */

const selectTodo = (todoId) => {
  selectedTodoId.value = todoId
}

const handleTodoBackspace = async (
  todo,
  event,
) => {
  const currentTitle =
    todoTitles.value[todo.id] ?? ''

  if (currentTitle.length !== 0) {
    return
  }

  event.preventDefault()

  await deleteTodo(todo.id)
}

const isTextInput = (element) => {
  if (!element) {
    return false
  }

  return (
    element.tagName === 'INPUT'
    || element.tagName === 'TEXTAREA'
    || element.isContentEditable
  )
}

const handleGlobalKeydown = async (event) => {
  const target = event.target

  /*
   * Bir input içerisindeysek browser'ın normal
   * yazma/silme davranışına karışmıyoruz.
   */
  if (isTextInput(target)) {
    return
  }

  /*
   * Seçili Todo varsa Delete veya Backspace
   * doğrudan o Todo'yu siler.
   */
  if (
    selectedTodoId.value
    && (
      event.key === 'Delete'
      || event.key === 'Backspace'
    )
    && authStore.can('todos.delete')
  ) {
    event.preventDefault()

    await deleteTodo(
      selectedTodoId.value,
    )

    return
  }

  /*
   * Browser shortcut'larına karışmıyoruz.
   */
  if (
    event.ctrlKey
    || event.metaKey
    || event.altKey
  ) {
    return
  }

  /*
   * Normal bir karakter yazıldıysa kullanıcıyı
   * Add Todo input'una otomatik geçiriyoruz.
   */
  if (
    event.key.length === 1
    && authStore.can('todos.create')
  ) {
    if (
      !newTodoTitle.value
      && event.key === ' '
    ) {
      return
    }

    event.preventDefault()

    selectedTodoId.value = null

    newTodoTitle.value += event.key

    await nextTick()

    newTodoInput.value?.focus()
  }
}

/* -------------------------
   HELPERS
------------------------- */

const isUpdating = (todoId) => {
  return updatingTodoIds.value.includes(todoId)
}

const isDeleting = (todoId) => {
  return deletingTodoIds.value.includes(todoId)
}

watch(
  () => route.params.id,
  (userId) => {
    if (!userId) {
      return
    }

    todos.value = []
    todoTitles.value = {}
    newTodoTitle.value = ''
    selectedTodoId.value = null

    fetchTodos(userId)
  },
  {
    immediate: true,
  },
)

onMounted(() => {
  document.addEventListener(
    'keydown',
    handleGlobalKeydown,
  )
})

onBeforeUnmount(() => {
  document.removeEventListener(
    'keydown',
    handleGlobalKeydown,
  )
})
</script>

<template>
  <section class="todo-page">
    <h1>Todos</h1>

    <p
      v-if="errorMessage"
      class="todo-state todo-state--error"
    >
      {{ errorMessage }}
    </p>

    <p
      v-if="isLoading"
      class="todo-state"
    >
      Loading todos...
    </p>

    <template v-else>
      <div class="todo-list">
        <div
          v-for="todo in todos"
          :key="todo.id"
          class="todo-row"
          :class="{
            'todo-row--selected':
              selectedTodoId === todo.id,
          }"
          @click="selectTodo(todo.id)"
        >
          <input
            type="checkbox"
            class="todo-checkbox"
            :checked="todo.completed"
            :disabled="
              isUpdating(todo.id)
              || !authStore.can('todos.update')
            "
            @click.stop
            @change="toggleTodo(todo)"
          />

          <input
            v-model="todoTitles[todo.id]"
            type="text"
            class="todo-title-input"
            :class="{
              'todo-title-input--completed':
                todo.completed,
            }"
            :readonly="
              !authStore.can('todos.update')
            "
            maxlength="200"
            autocomplete="off"
            @focus="selectTodo(todo.id)"
            @click.stop="selectTodo(todo.id)"
            @blur="saveTodoTitle(todo)"
            @keydown.enter.prevent="
              saveTodoTitle(todo)
            "
            @keydown.esc.prevent="
              resetTodoTitle(todo)
            "
            @keydown.backspace="
              handleTodoBackspace(todo, $event)
            "
          />

          <button
            v-if="authStore.can('todos.delete')"
            type="button"
            class="todo-delete"
            :disabled="isDeleting(todo.id)"
            aria-label="Delete todo"
            @click.stop="deleteTodo(todo.id)"
          >
            <IconTrash
              :size="16"
              :stroke-width="1.7"
            />
          </button>
        </div>
      </div>

      <form
        v-if="authStore.can('todos.create')"
        class="todo-create"
        @submit.prevent="createTodo"
      >
        <IconPlus
          class="todo-create__icon"
          :size="18"
          :stroke-width="1.8"
        />

        <input
          ref="newTodoInput"
          v-model="newTodoTitle"
          type="text"
          class="todo-create__input"
          placeholder="Start typing..."
          maxlength="200"
          autocomplete="off"
          :disabled="isCreating"
          @focus="selectedTodoId = null"
        />
      </form>

      <p
        v-if="
          todos.length === 0
          && !authStore.can('todos.create')
        "
        class="todo-state"
      >
        No todos found.
      </p>
    </template>
  </section>
</template>

<style scoped>
.todo-page {
  width: 100%;
}

.todo-page h1 {
  margin: 0 0 26px;

  color: var(--color-title);
  font-size: 28px;
  font-weight: 700;
}

.todo-state {
  margin: 0 0 16px;

  color: var(--color-subtitle);
  font-size: 13px;
}

.todo-state--error {
  color: #b42318;
}

/* -------------------------
   TODO LIST
------------------------- */

.todo-list {
  border-top:
    1px solid var(--color-border);
}

.todo-row {
  min-height: 52px;

  display: flex;
  align-items: center;
  gap: 12px;

  padding: 0 10px;

  border-bottom:
    1px solid var(--color-border);

  border-radius: 7px;

  transition:
    background-color 0.15s ease;
}

.todo-row--selected {
  background:
    rgba(82, 63, 158, 0.045);
}

.todo-title-input {
  min-width: 0;
  flex: 1;

  padding: 14px 0;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;
  line-height: 1.5;

  background: transparent;
  border: 0;
  outline: none;
}

.todo-title-input--completed {
  color: var(--color-subtitle);

  text-decoration: line-through;

  opacity: 0.7;
}

.todo-title-input[readonly] {
  cursor: default;
}

.todo-checkbox {
  width: 16px;
  height: 16px;

  flex-shrink: 0;

  accent-color: var(--color-primary);

  cursor: pointer;
}

.todo-checkbox:disabled {
  cursor: wait;
}


/* -------------------------
   DELETE
------------------------- */

.todo-delete {
  width: 30px;
  height: 30px;

  flex-shrink: 0;

  display: grid;
  place-items: center;

  padding: 0;

  color: #9096a2;

  background: transparent;
  border: 0;
  border-radius: 7px;

  cursor: pointer;

  opacity: 0;

  transition:
    opacity 0.18s ease,
    color 0.18s ease,
    background-color 0.18s ease;
}

.todo-row:hover .todo-delete,
.todo-delete:focus-visible {
  opacity: 1;
}

.todo-delete:hover {
  color: #b42318;

  background:
    rgba(180, 35, 24, 0.07);
}

.todo-delete:disabled {
  cursor: wait;
  opacity: 0.4;
}

/* -------------------------
   CREATE TODO
------------------------- */

.todo-create {
  min-height: 52px;

  display: flex;
  align-items: center;
  gap: 10px;

  padding: 0 10px;

  border-bottom:
    1px solid var(--color-border);
}

.todo-create__icon {
  flex-shrink: 0;

  color: var(--color-primary);
}

.todo-create__input {
  width: 100%;

  padding: 13px 0;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;

  background: transparent;
  border: 0;
  outline: none;
}

.todo-create__input::placeholder {
  color: #a0a5ae;
}

.todo-create__input:disabled {
  opacity: 0.6;
}
</style>