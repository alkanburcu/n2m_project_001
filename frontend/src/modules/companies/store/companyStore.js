import {
  computed,
  ref,
} from 'vue'

import { defineStore } from 'pinia'

import companyService from '../services/companyService'


export const useCompanyStore = defineStore(
  'companies',
  () => {
    const companies = ref([])

    const searchTerm = ref('')
    const currentPage = ref(1)
    const totalCount = ref(0)
    const nextPageUrl = ref(null)

    const isLoading = ref(false)
    const isLoadingMore = ref(false)
    const isCreating = ref(false)

    const error = ref(null)

    const hasMore = computed(() => {
      return Boolean(nextPageUrl.value)
    })


    const fetchCompanies = async ({
      search = '',
      pageSize = 20,
    } = {}) => {
      isLoading.value = true
      error.value = null

      try {
        searchTerm.value = search
        currentPage.value = 1

        const response =
          await companyService.getCompanies({
            search,
            page: 1,
            pageSize,
          })

        companies.value =
          response.data.results

        totalCount.value =
          response.data.count

        nextPageUrl.value =
          response.data.next

        return companies.value
      } catch (err) {
        error.value =
          'Companies could not be loaded.'

        throw err
      } finally {
        isLoading.value = false
      }
    }


    const loadMore = async ({
      pageSize = 20,
    } = {}) => {
      if (
        !hasMore.value
        || isLoadingMore.value
      ) {
        return
      }

      isLoadingMore.value = true
      error.value = null

      try {
        const nextPage =
          currentPage.value + 1

        const response =
          await companyService.getCompanies({
            search: searchTerm.value,
            page: nextPage,
            pageSize,
          })

        const existingIds = new Set(
          companies.value.map(
            (company) => company.id,
          ),
        )

        const newCompanies =
          response.data.results.filter(
            (company) => {
              return !existingIds.has(
                company.id,
              )
            },
          )

        companies.value.push(
          ...newCompanies,
        )

        currentPage.value =
          nextPage

        totalCount.value =
          response.data.count

        nextPageUrl.value =
          response.data.next
      } catch (err) {
        error.value =
          'More companies could not be loaded.'

        throw err
      } finally {
        isLoadingMore.value = false
      }
    }


    const createCompany = async (
      payload,
    ) => {
      isCreating.value = true
      error.value = null

      try {
        const response =
          await companyService.createCompany(
            payload,
          )

        const company =
          response.data

        const alreadyExists =
          companies.value.some(
            (item) => {
              return item.id === company.id
            },
          )

        if (!alreadyExists) {
          companies.value.unshift(
            company,
          )

          totalCount.value += 1
        }

        return company
      } catch (err) {
        error.value =
          'Company could not be created.'

        throw err
      } finally {
        isCreating.value = false
      }
    }


    const resetCompanies = () => {
      companies.value = []
      searchTerm.value = ''
      currentPage.value = 1
      totalCount.value = 0
      nextPageUrl.value = null
      error.value = null
    }


    return {
      companies,
      searchTerm,
      totalCount,

      isLoading,
      isLoadingMore,
      isCreating,

      error,
      hasMore,

      fetchCompanies,
      loadMore,
      createCompany,
      resetCompanies,
    }
  },
)