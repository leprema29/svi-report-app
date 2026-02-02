<template>
  <v-container>
    <!-- Upload Section -->
    <v-card class="mb-6" elevation="2">
      <v-card-title class="bg-primary text-white">
        <v-icon left color="white">mdi-upload</v-icon>
        Télécharger un Nouveau Rapport (PDF ou PPTX)
      </v-card-title>

      <v-card-text class="pt-4">
        <v-form ref="uploadForm" v-model="valid">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="uploadData.title"
                label="Titre du Rapport"
                :rules="[rules.required]"
                prepend-icon="mdi-text"
                outlined
                dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-file-input
                v-model="uploadData.file"
                label="Fichier (PDF ou PPTX)"
                accept=".pdf,.pptx"
                :rules="[rules.required]"
                prepend-icon="mdi-file-document"
                outlined
                dense
                show-size
              >
                <template v-slot:selection="{ fileNames }">
                  <v-chip
                    v-for="fileName in fileNames"
                    :key="fileName"
                    :color="getFileTypeColor(fileName)"
                    small
                    label
                    class="me-2"
                  >
                    <v-icon left small>{{ getFileTypeIcon(fileName) }}</v-icon>
                    {{ fileName }}
                  </v-chip>
                </template>
              </v-file-input>
            </v-col>
          </v-row>

          <v-btn
            color="primary"
            @click="uploadReport"
            :loading="uploading"
            :disabled="!valid || uploading"
            large
          >
            <v-icon left>mdi-cloud-upload</v-icon>
            Télécharger et Analyser
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Reports List -->
    <v-card elevation="2">
      <v-card-title class="bg-secondary text-white">
        <v-icon left color="white">mdi-file-document-multiple</v-icon>
        Rapports de Surveillance

        <v-spacer></v-spacer>

        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Rechercher"
          single-line
          hide-details
          dark
          dense
          class="mt-0 pt-0"
          style="max-width: 300px;"
        ></v-text-field>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="reports"
          :search="search"
          :loading="loading"
          :items-per-page="10"
          class="elevation-1"
        >
          <!-- File Type Column -->
          <template v-slot:item.file_type="{ item }">
            <v-chip
              :color="item.file_type === 'pptx' ? 'orange' : 'red'"
              dark
              small
            >
              <v-icon left small>{{ item.file_type === 'pptx' ? 'mdi-file-powerpoint' : 'mdi-file-pdf-box' }}</v-icon>
              {{ item.file_type?.toUpperCase() || 'PDF' }}
            </v-chip>
          </template>

          <!-- Status Column -->
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getStatusColor(item.status)"
              dark
              small
            >
              <v-icon left small>{{ getStatusIcon(item.status) }}</v-icon>
              {{ getStatusText(item.status) }}
            </v-chip>
          </template>

          <!-- Period Column -->
          <template v-slot:item.period="{ item }">
            <span v-if="item.period_start && item.period_end">
              {{ formatDate(item.period_start) }} - {{ formatDate(item.period_end) }}
            </span>
            <span v-else class="text-grey">N/A</span>
          </template>

          <!-- Mentions Column -->
          <template v-slot:item.total_mentions="{ item }">
            <div>
              <strong>{{ item.total_mentions || 0 }}</strong>
              <v-chip
                v-if="item.mentions_change_percent"
                :color="item.mentions_change_percent > 0 ? 'success' : 'error'"
                x-small
                class="ml-1"
              >
                {{ item.mentions_change_percent > 0 ? '+' : '' }}{{ item.mentions_change_percent }}%
              </v-chip>
            </div>
          </template>

          <!-- Reach Column -->
          <template v-slot:item.total_reach="{ item }">
            <div>
              <strong>{{ formatNumber(item.total_reach || 0) }}</strong>
              <v-chip
                v-if="item.reach_change_percent"
                :color="item.reach_change_percent > 0 ? 'success' : 'error'"
                x-small
                class="ml-1"
              >
                {{ item.reach_change_percent > 0 ? '+' : '' }}{{ item.reach_change_percent }}%
              </v-chip>
            </div>
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              @click="viewDetails(item)"
              title="Voir Détails"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>

            <v-btn
              icon
              small
              @click="downloadDocx(item)"
              :disabled="item.status !== 'completed'"
              color="success"
              title="Télécharger Word"
            >
              <v-icon small>mdi-file-word</v-icon>
            </v-btn>

            <v-btn
              icon
              small
              @click="deleteReport(item)"
              color="error"
              title="Supprimer"
            >
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="1100px">
      <v-card v-if="selectedReport">
        <v-card-title class="bg-primary text-white">
          <span class="text-h5">{{ selectedReport.title }}</span>
          <v-spacer></v-spacer>
          <v-chip
            :color="selectedReport.file_type === 'pptx' ? 'orange' : 'red'"
            dark
            small
            class="mr-2"
          >
            {{ selectedReport.file_type?.toUpperCase() || 'PDF' }}
          </v-chip>
          <v-btn icon dark @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text class="pt-4">
          <!-- Period -->
          <v-row class="mb-3">
            <v-col cols="12">
              <h3>Période</h3>
              <p class="text-h6">
                {{ formatDate(selectedReport.period_start) }} - {{ formatDate(selectedReport.period_end) }}
              </p>
            </v-col>
          </v-row>

          <!-- KPI Section 1: Indicateurs de présence passive -->
          <v-row class="mt-4">
            <v-col cols="12">
              <h3 class="mb-3">1. Indicateurs de présence passive</h3>
              <v-simple-table dense class="elevation-1">
                <template v-slot:default>
                  <thead>
                    <tr class="bg-blue-lighten-4">
                      <th class="text-left">Indicateur</th>
                      <th class="text-right">Valeur</th>
                      <th class="text-right">Évolution</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Nombre de Followers</td>
                      <td class="text-right">{{ formatNumber(getPresencePassive('followers')) }}</td>
                      <td class="text-right">
                        <v-chip
                          v-if="getPresencePassive('followers_evolution')"
                          :color="getPresencePassive('followers_evolution') > 0 ? 'success' : 'error'"
                          x-small
                        >
                          {{ getPresencePassive('followers_evolution') > 0 ? '+' : '' }}{{ getPresencePassive('followers_evolution') }}%
                        </v-chip>
                        <span v-else>N/A</span>
                      </td>
                    </tr>
                    <tr>
                      <td>Nombre de Vues/Impressions</td>
                      <td class="text-right">{{ formatNumber(getPresencePassive('views')) }}</td>
                      <td class="text-right">
                        <v-chip
                          v-if="getPresencePassive('views_evolution')"
                          :color="getPresencePassive('views_evolution') > 0 ? 'success' : 'error'"
                          x-small
                        >
                          {{ getPresencePassive('views_evolution') > 0 ? '+' : '' }}{{ getPresencePassive('views_evolution') }}%
                        </v-chip>
                        <span v-else>N/A</span>
                      </td>
                    </tr>
                    <tr>
                      <td>Portée Potentielle (Potential Reach)</td>
                      <td class="text-right">{{ formatNumber(getPresencePassive('potential_reach')) }}</td>
                      <td class="text-right">
                        <v-chip
                          v-if="getPresencePassive('reach_evolution')"
                          :color="getPresencePassive('reach_evolution') > 0 ? 'success' : 'error'"
                          x-small
                        >
                          {{ getPresencePassive('reach_evolution') > 0 ? '+' : '' }}{{ getPresencePassive('reach_evolution') }}%
                        </v-chip>
                        <span v-else>N/A</span>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>
          </v-row>

          <!-- KPI Section 2: Indicateurs de présence active -->
          <v-row class="mt-4">
            <v-col cols="12">
              <h3 class="mb-3">2. Indicateurs de présence active</h3>
              <v-simple-table dense class="elevation-1">
                <template v-slot:default>
                  <thead>
                    <tr class="bg-green-lighten-4">
                      <th class="text-left">Indicateur</th>
                      <th class="text-right">Valeur</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Nombre de Commentaires</td>
                      <td class="text-right">{{ formatNumber(getPresenceActive('comments')) }}</td>
                    </tr>
                    <tr>
                      <td>Nombre de Likes (J'aime)</td>
                      <td class="text-right">{{ formatNumber(getPresenceActive('likes')) }}</td>
                    </tr>
                    <tr>
                      <td>Nombre de Partages (Shares)</td>
                      <td class="text-right">{{ formatNumber(getPresenceActive('shares')) }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>
          </v-row>

          <!-- KPI Section 3: Indicateurs des tendances d'opinions -->
          <v-row class="mt-4">
            <v-col cols="12">
              <h3 class="mb-3">3. Indicateurs des tendances d'opinions</h3>
              <v-simple-table dense class="elevation-1">
                <template v-slot:default>
                  <thead>
                    <tr class="bg-orange-lighten-4">
                      <th class="text-left">Tendance</th>
                      <th class="text-right">Nombre</th>
                      <th class="text-right">Pourcentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <v-icon small color="success" class="mr-1">mdi-emoticon-happy</v-icon>
                        Positif
                      </td>
                      <td class="text-right">{{ getSentiment('positive') }}</td>
                      <td class="text-right">{{ getSentimentPercentage('positive') }}%</td>
                    </tr>
                    <tr>
                      <td>
                        <v-icon small color="grey" class="mr-1">mdi-emoticon-neutral</v-icon>
                        Neutre
                      </td>
                      <td class="text-right">{{ getSentiment('neutral') }}</td>
                      <td class="text-right">{{ getSentimentPercentage('neutral') }}%</td>
                    </tr>
                    <tr>
                      <td>
                        <v-icon small color="error" class="mr-1">mdi-emoticon-sad</v-icon>
                        Négatif
                      </td>
                      <td class="text-right">{{ getSentiment('negative') }}</td>
                      <td class="text-right">{{ getSentimentPercentage('negative') }}%</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>
          </v-row>

          <!-- Sources -->
          <v-row v-if="selectedReport.sources_data && Object.keys(selectedReport.sources_data).length" class="mt-4">
            <v-col cols="12">
              <h3 class="mb-3">4. Répartition par Source</h3>
              <v-simple-table dense class="elevation-1">
                <template v-slot:default>
                  <thead>
                    <tr class="bg-purple-lighten-4">
                      <th class="text-left">Plateforme</th>
                      <th class="text-right">Mentions</th>
                      <th class="text-right">Pourcentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(value, key) in selectedReport.sources_data" :key="key">
                      <td>
                        <v-icon small class="mr-1">{{ getPlatformIcon(key) }}</v-icon>
                        {{ key }}
                      </td>
                      <td class="text-right">{{ formatNumber(value) }}</td>
                      <td class="text-right">{{ getSourcePercentage(key) }}%</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>
          </v-row>

          <!-- Topics -->
          <v-row v-if="selectedReport.topics_data && selectedReport.topics_data.length" class="mt-4">
            <v-col cols="12">
              <h3 class="mb-3">5. Sujets Principaux</h3>
              <v-chip-group>
                <v-chip
                  v-for="topic in selectedReport.topics_data.slice(0, 15)"
                  :key="topic.name"
                  color="orange"
                  text-color="white"
                >
                  {{ topic.name }}: {{ topic.count }}
                </v-chip>
              </v-chip-group>
            </v-col>
          </v-row>

          <!-- Hashtags -->
          <v-row v-if="selectedReport.hashtags_data && selectedReport.hashtags_data.length" class="mt-4">
            <v-col cols="12">
              <h3 class="mb-3">6. Hashtags Populaires</h3>
              <v-chip-group>
                <v-chip
                  v-for="hashtag in selectedReport.hashtags_data.slice(0, 10)"
                  :key="hashtag.hashtag"
                  color="purple"
                  text-color="white"
                >
                  {{ hashtag.hashtag }}: {{ hashtag.count }}
                </v-chip>
              </v-chip-group>
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="downloadDocx(selectedReport)" :disabled="selectedReport.status !== 'completed'">
            <v-icon left>mdi-file-word</v-icon>
            Télécharger Word
          </v-btn>
          <v-btn text @click="detailsDialog = false">Fermer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      top
    >
      {{ snackbar.message }}
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar.show = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ReportExtractor',

  data() {
    return {
      valid: false,
      loading: false,
      uploading: false,
      search: '',
      reports: [],
      detailsDialog: false,
      selectedReport: null,

      uploadData: {
        title: '',
        file: null,
      },

      rules: {
        required: value => !!value || 'Champ requis',
      },

      headers: [
        { title: 'ID', key: 'id', sortable: true },
        { title: 'Type', key: 'file_type', sortable: true },
        { title: 'Titre', key: 'title', sortable: true },
        { title: 'Statut', key: 'status', sortable: true },
        { title: 'Période', key: 'period', sortable: false },
        { title: 'Mentions', key: 'total_mentions', sortable: true },
        { title: 'Portée', key: 'total_reach', sortable: true },
        { title: 'Créé le', key: 'created_at', sortable: true },
        { title: 'Actions', key: 'actions', sortable: false },
      ],

      snackbar: {
        show: false,
        message: '',
        color: 'success',
      },

      refreshInterval: null,
    }
  },

  mounted() {
    this.loadReports()
    // Auto-refresh every 10 seconds
    this.refreshInterval = setInterval(() => {
      this.loadReports(true)
    }, 10000)
  },

  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },

  methods: {
    async loadReports(silent = false) {
      if (!silent) {
        this.loading = true
      }

      try {
        const response = await axios.get('/api/reports/')
        this.reports = response.data.results || response.data
      } catch (error) {
        console.error('Error loading reports:', error)
        if (!silent) {
          this.showSnackbar('Erreur lors du chargement des rapports', 'error')
        }
      } finally {
        if (!silent) {
          this.loading = false
        }
      }
    },

    async uploadReport() {
      if (!this.$refs.uploadForm.validate()) {
        return
      }

      this.uploading = true

      try {
        const formData = new FormData()
        formData.append('title', this.uploadData.title)

        // Use the new field name for file upload
        const file = this.uploadData.file[0]
        const fileExtension = file.name.split('.').pop().toLowerCase()

        if (fileExtension === 'pptx') {
          formData.append('original_file', file)
        } else {
          // For PDF, use original_pdf for backwards compatibility
          formData.append('original_pdf', file)
        }

        await axios.post('/api/reports/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        this.showSnackbar('Rapport téléchargé avec succès! Traitement en cours...', 'success')
        this.uploadData.title = ''
        this.uploadData.file = null
        this.$refs.uploadForm.reset()
        this.loadReports()
      } catch (error) {
        console.error('Error uploading report:', error)
        this.showSnackbar('Erreur lors du téléchargement du rapport', 'error')
      } finally {
        this.uploading = false
      }
    },

    viewDetails(report) {
      this.selectedReport = report
      this.detailsDialog = true
    },

    async downloadDocx(report) {
      if (report.status !== 'completed') {
        this.showSnackbar('Le rapport n\'est pas encore terminé', 'warning')
        return
      }

      try {
        const response = await axios.get(`/api/reports/${report.id}/download-docx/`, {
          responseType: 'blob',
        })

        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `rapport_${report.id}.docx`)
        document.body.appendChild(link)
        link.click()
        link.remove()

        this.showSnackbar('Document Word téléchargé', 'success')
      } catch (error) {
        console.error('Error downloading DOCX:', error)
        this.showSnackbar('Erreur lors du téléchargement du document Word', 'error')
      }
    },

    async deleteReport(report) {
      if (!confirm(`Êtes-vous sûr de vouloir supprimer le rapport "${report.title}"?`)) {
        return
      }

      try {
        await axios.delete(`/api/reports/${report.id}/`)
        this.showSnackbar('Rapport supprimé', 'success')
        this.loadReports()
      } catch (error) {
        console.error('Error deleting report:', error)
        this.showSnackbar('Erreur lors de la suppression du rapport', 'error')
      }
    },

    // Helper methods for new KPI structure
    getPresencePassive(key) {
      if (!this.selectedReport || !this.selectedReport.presence_passive_data) {
        return 0
      }
      return this.selectedReport.presence_passive_data[key] || 0
    },

    getPresenceActive(key) {
      if (!this.selectedReport || !this.selectedReport.presence_active_data) {
        return 0
      }
      return this.selectedReport.presence_active_data[key] || 0
    },

    getSentiment(key) {
      if (!this.selectedReport || !this.selectedReport.sentiment_data) {
        return 0
      }
      return this.selectedReport.sentiment_data[key] || 0
    },

    getSentimentPercentage(key) {
      if (!this.selectedReport || !this.selectedReport.sentiment_data) {
        return '0.00'
      }
      const total = Object.values(this.selectedReport.sentiment_data).reduce((a, b) => a + b, 0)
      if (total === 0) return '0.00'
      const value = this.selectedReport.sentiment_data[key] || 0
      return ((value / total) * 100).toFixed(2)
    },

    getSourcePercentage(key) {
      if (!this.selectedReport || !this.selectedReport.sources_data) {
        return '0.00'
      }
      const total = Object.values(this.selectedReport.sources_data).reduce((a, b) => a + b, 0)
      if (total === 0) return '0.00'
      const value = this.selectedReport.sources_data[key] || 0
      return ((value / total) * 100).toFixed(2)
    },

    getFileTypeColor(fileName) {
      if (fileName.toLowerCase().endsWith('.pptx')) {
        return 'orange'
      }
      return 'red'
    },

    getFileTypeIcon(fileName) {
      if (fileName.toLowerCase().endsWith('.pptx')) {
        return 'mdi-file-powerpoint'
      }
      return 'mdi-file-pdf-box'
    },

    getPlatformIcon(platform) {
      const icons = {
        'Facebook': 'mdi-facebook',
        'Instagram': 'mdi-instagram',
        'Twitter': 'mdi-twitter',
        'X': 'mdi-twitter',
        'X (Twitter)': 'mdi-twitter',
        'TikTok': 'mdi-music-note',
        'YouTube': 'mdi-youtube',
        'LinkedIn': 'mdi-linkedin',
        'WhatsApp': 'mdi-whatsapp',
        'Telegram': 'mdi-telegram',
      }
      return icons[platform] || 'mdi-web'
    },

    getStatusColor(status) {
      const colors = {
        pending: 'orange',
        processing: 'blue',
        completed: 'success',
        failed: 'error',
      }
      return colors[status] || 'grey'
    },

    getStatusIcon(status) {
      const icons = {
        pending: 'mdi-clock-outline',
        processing: 'mdi-refresh',
        completed: 'mdi-check-circle',
        failed: 'mdi-alert-circle',
      }
      return icons[status] || 'mdi-help-circle'
    },

    getStatusText(status) {
      const texts = {
        pending: 'En Attente',
        processing: 'En Cours',
        completed: 'Terminé',
        failed: 'Échoué',
      }
      return texts[status] || status
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('fr-FR')
    },

    formatNumber(num) {
      if (!num) return '0'
      return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    },

    showSnackbar(message, color = 'success') {
      this.snackbar.message = message
      this.snackbar.color = color
      this.snackbar.show = true
    },
  },
}
</script>

<style scoped>
.v-card-title {
  font-weight: bold;
}

.v-simple-table th {
  font-weight: bold !important;
}
</style>
