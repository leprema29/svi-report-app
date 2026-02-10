<template>
  <v-container>
    <!-- Tab Navigation -->
    <v-tabs v-model="activeTab" class="mb-4" color="primary">
      <v-tab value="single">
        <v-icon left>mdi-file-document</v-icon>
        Rapport Unique
      </v-tab>
      <v-tab value="multi">
        <v-icon left>mdi-file-document-multiple</v-icon>
        Rapports Multiples (Consolidé)
      </v-tab>
    </v-tabs>

    <!-- Single Upload Section -->
    <v-card class="mb-6" elevation="2" v-show="activeTab === 'single'">
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

    <!-- Multi-Report Upload Section -->
    <v-card class="mb-6" elevation="2" v-show="activeTab === 'multi'">
      <v-card-title class="bg-deep-purple text-white">
        <v-icon left color="white">mdi-file-document-multiple</v-icon>
        Créer un Rapport Consolidé (Plusieurs Sources)
      </v-card-title>

      <v-card-text class="pt-4">
        <v-alert type="info" variant="tonal" class="mb-4">
          <strong>Rapport Consolidé:</strong> Téléchargez plusieurs rapports (Mention.com PDF et/ou Brand24 PPTX)
          avec le même mot-clé/alerte pour générer un rapport Word unique combinant toutes les données.
        </v-alert>

        <v-form ref="multiUploadForm" v-model="multiValid">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="multiUploadData.title"
                label="Titre/Mot-clé commun"
                :rules="[rules.required]"
                prepend-icon="mdi-text"
                outlined
                dense
                hint="Le titre commun pour tous les rapports de ce groupe"
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-file-input
                v-model="multiUploadData.files"
                label="Fichiers (PDF ou PPTX)"
                accept=".pdf,.pptx"
                :rules="[rules.required, rules.minFiles]"
                prepend-icon="mdi-file-document-multiple"
                outlined
                dense
                show-size
                multiple
                chips
              >
                <template v-slot:selection="{ fileNames }">
                  <v-chip
                    v-for="fileName in fileNames"
                    :key="fileName"
                    :color="getFileTypeColor(fileName)"
                    small
                    label
                    class="me-2 mb-1"
                    closable
                    @click:close="removeFile(fileName)"
                  >
                    <v-icon left small>{{ getFileTypeIcon(fileName) }}</v-icon>
                    {{ fileName }}
                  </v-chip>
                </template>
              </v-file-input>
            </v-col>
          </v-row>

          <!-- Manual Entry Fields -->
          <v-expansion-panels variant="accordion" class="mb-4">
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-pencil-plus</v-icon>
                Entrées manuelles (KPIs supplémentaires)
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-alert type="warning" variant="tonal" class="mb-3" density="compact">
                  Utilisez ces champs pour ajouter des valeurs qui ne sont pas disponibles dans les rapports sources.
                </v-alert>
                <v-row>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="multiUploadData.manual_followers"
                      label="Followers"
                      type="number"
                      prepend-icon="mdi-account-multiple"
                      outlined
                      dense
                      clearable
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="multiUploadData.manual_likes"
                      label="Likes"
                      type="number"
                      prepend-icon="mdi-thumb-up"
                      outlined
                      dense
                      clearable
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="multiUploadData.manual_shares"
                      label="Partages"
                      type="number"
                      prepend-icon="mdi-share-variant"
                      outlined
                      dense
                      clearable
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="multiUploadData.manual_comments"
                      label="Commentaires"
                      type="number"
                      prepend-icon="mdi-comment-multiple"
                      outlined
                      dense
                      clearable
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="multiUploadData.manual_views"
                      label="Vues"
                      type="number"
                      prepend-icon="mdi-eye"
                      outlined
                      dense
                      clearable
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <v-btn
            color="deep-purple"
            @click="uploadMultiReport"
            :loading="uploadingMulti"
            :disabled="!multiValid || uploadingMulti"
            large
          >
            <v-icon left>mdi-cloud-upload</v-icon>
            Créer Rapport Consolidé
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Report Groups List (Multi-reports) -->
    <v-card elevation="2" class="mb-6" v-show="activeTab === 'multi' && reportGroups.length > 0">
      <v-card-title class="bg-deep-purple-lighten-1 text-white">
        <v-icon left color="white">mdi-folder-multiple</v-icon>
        Rapports Consolidés
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="groupHeaders"
          :items="reportGroups"
          :items-per-page="5"
          class="elevation-1"
        >
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

          <!-- Source Count -->
          <template v-slot:item.source_count="{ item }">
            <v-chip small color="info" variant="outlined">
              {{ item.source_count || item.source_filenames?.length || 0 }} fichiers
            </v-chip>
          </template>

          <!-- Source Files -->
          <template v-slot:item.source_filenames="{ item }">
            <div class="d-flex flex-wrap ga-1">
              <v-chip
                v-for="filename in (item.source_filenames || []).slice(0, 2)"
                :key="filename"
                :color="getFileTypeColor(filename)"
                x-small
                label
              >
                {{ filename.substring(0, 15) }}{{ filename.length > 15 ? '...' : '' }}
              </v-chip>
              <v-chip v-if="(item.source_filenames || []).length > 2" x-small color="grey">
                +{{ item.source_filenames.length - 2 }}
              </v-chip>
            </div>
          </template>

          <!-- Period Column -->
          <template v-slot:item.period="{ item }">
            <span v-if="item.period_start && item.period_end">
              {{ formatDate(item.period_start) }} - {{ formatDate(item.period_end) }}
            </span>
            <span v-else class="text-grey">N/A</span>
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <div class="d-flex align-center ga-1">
              <v-tooltip location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-microsoft-word"
                    size="small"
                    variant="tonal"
                    color="deep-purple"
                    :disabled="item.status !== 'completed'"
                    @click="downloadGroupDocx(item)"
                  ></v-btn>
                </template>
                <span>Télécharger Word Consolidé</span>
              </v-tooltip>

              <v-tooltip location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-trash-can-outline"
                    size="small"
                    variant="tonal"
                    color="error"
                    @click="deleteReportGroup(item)"
                  ></v-btn>
                </template>
                <span>Supprimer</span>
              </v-tooltip>
            </div>
          </template>
        </v-data-table>
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

          <!-- Original File Name Column -->
          <template v-slot:item.original_file_name="{ item }">
            <v-tooltip bottom v-if="item.original_file_name">
              <template v-slot:activator="{ props }">
                <span v-bind="props" class="text-truncate" style="max-width: 150px; display: inline-block;">
                  {{ item.original_file_name }}
                </span>
              </template>
              <span>{{ item.original_file_name }}</span>
            </v-tooltip>
            <span v-else class="text-grey">N/A</span>
          </template>

          <!-- Report Type Column -->
          <template v-slot:item.report_type="{ item }">
            <v-chip
              :color="getReportTypeColor(item.report_type)"
              small
              variant="outlined"
            >
              <v-icon left small>{{ getReportTypeIcon(item.report_type) }}</v-icon>
              {{ getReportTypeLabel(item.report_type) }}
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

          <!-- Created At Column -->
          <template v-slot:item.created_at="{ item }">
            <div class="text-caption">
              <v-icon size="x-small" class="mr-1">mdi-calendar</v-icon>
              {{ formatDateTime(item.created_at) }}
            </div>
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <div class="d-flex align-center ga-1">
              <v-tooltip location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-eye-outline"
                    size="small"
                    variant="tonal"
                    color="info"
                    @click="viewDetails(item)"
                  ></v-btn>
                </template>
                <span>Voir Détails</span>
              </v-tooltip>

              <v-tooltip location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-microsoft-word"
                    size="small"
                    variant="tonal"
                    color="primary"
                    :disabled="item.status !== 'completed'"
                    @click="downloadDocx(item)"
                  ></v-btn>
                </template>
                <span>Télécharger Word</span>
              </v-tooltip>

              <v-tooltip location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-trash-can-outline"
                    size="small"
                    variant="tonal"
                    color="error"
                    @click="deleteReport(item)"
                  ></v-btn>
                </template>
                <span>Supprimer</span>
              </v-tooltip>
            </div>
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
          <!-- Report Type Info -->
          <v-alert
            v-if="selectedReport.report_type"
            :color="getReportTypeColor(selectedReport.report_type)"
            variant="tonal"
            class="mb-4"
          >
            <div class="d-flex align-center">
              <v-icon :color="getReportTypeColor(selectedReport.report_type)" class="mr-2">
                {{ getReportTypeIcon(selectedReport.report_type) }}
              </v-icon>
              <div>
                <strong>{{ selectedReport.report_type_display || getReportTypeLabel(selectedReport.report_type) }}</strong>
                <div class="text-caption mt-1">
                  <span class="text-success mr-3" v-if="selectedReport.available_kpis?.length">
                    <v-icon x-small color="success">mdi-check</v-icon>
                    Disponible: {{ selectedReport.available_kpis.join(', ') }}
                  </span>
                  <span class="text-error" v-if="selectedReport.unavailable_kpis?.length">
                    <v-icon x-small color="error">mdi-close</v-icon>
                    Non disponible: {{ selectedReport.unavailable_kpis.slice(0, 5).join(', ') }}{{ selectedReport.unavailable_kpis.length > 5 ? '...' : '' }}
                  </span>
                </div>
              </div>
            </div>
          </v-alert>

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

          <!-- Demographics Section (for Brand24 Demographics reports) -->
          <template v-if="selectedReport.demographics_data && Object.keys(selectedReport.demographics_data).length">
            <!-- Gender Distribution -->
            <v-row v-if="selectedReport.demographics_data.gender" class="mt-4">
              <v-col cols="12" md="6">
                <h3 class="mb-3">7. Distribution par Genre</h3>
                <v-simple-table dense class="elevation-1">
                  <template v-slot:default>
                    <thead>
                      <tr class="bg-pink-lighten-4">
                        <th class="text-left">Genre</th>
                        <th class="text-right">Pourcentage</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><v-icon small color="pink" class="mr-1">mdi-gender-female</v-icon> Femme</td>
                        <td class="text-right">{{ selectedReport.demographics_data.gender.female || 0 }}%</td>
                      </tr>
                      <tr>
                        <td><v-icon small color="blue" class="mr-1">mdi-gender-male</v-icon> Homme</td>
                        <td class="text-right">{{ selectedReport.demographics_data.gender.male || 0 }}%</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-col>

              <!-- Age Distribution -->
              <v-col cols="12" md="6" v-if="selectedReport.demographics_data.age?.length">
                <h3 class="mb-3">8. Distribution par Âge</h3>
                <v-simple-table dense class="elevation-1">
                  <template v-slot:default>
                    <thead>
                      <tr class="bg-teal-lighten-4">
                        <th class="text-left">Tranche d'Âge</th>
                        <th class="text-right">Pourcentage</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="age in selectedReport.demographics_data.age" :key="age.age_group">
                        <td>{{ age.age_group }}</td>
                        <td class="text-right">{{ age.percentage }}%</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-col>
            </v-row>

            <!-- Countries Distribution -->
            <v-row v-if="selectedReport.demographics_data.countries?.length" class="mt-4">
              <v-col cols="12">
                <h3 class="mb-3">9. Distribution par Pays</h3>
                <v-simple-table dense class="elevation-1">
                  <template v-slot:default>
                    <thead>
                      <tr class="bg-cyan-lighten-4">
                        <th class="text-left">Pays</th>
                        <th class="text-right">Pourcentage</th>
                        <th class="text-right">Portée</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="country in selectedReport.demographics_data.countries.slice(0, 10)" :key="country.country">
                        <td>{{ country.country }}</td>
                        <td class="text-right">{{ country.percentage }}%</td>
                        <td class="text-right">{{ formatNumber(country.reach) }}</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-col>
            </v-row>

            <!-- Interests -->
            <v-row v-if="selectedReport.demographics_data.interests?.length" class="mt-4">
              <v-col cols="12">
                <h3 class="mb-3">10. Centres d'Intérêt</h3>
                <v-chip-group>
                  <v-chip
                    v-for="interest in selectedReport.demographics_data.interests.slice(0, 10)"
                    :key="interest.interest"
                    color="teal"
                    text-color="white"
                  >
                    {{ interest.interest }}: {{ interest.percentage }}%
                  </v-chip>
                </v-chip-group>
              </v-col>
            </v-row>
          </template>
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
      activeTab: 'single',
      valid: false,
      multiValid: false,
      loading: false,
      uploading: false,
      uploadingMulti: false,
      search: '',
      reports: [],
      reportGroups: [],
      detailsDialog: false,
      selectedReport: null,

      uploadData: {
        title: '',
        file: null,
      },

      multiUploadData: {
        title: '',
        files: [],
        manual_followers: null,
        manual_likes: null,
        manual_shares: null,
        manual_comments: null,
        manual_views: null,
      },

      rules: {
        required: value => !!value || 'Champ requis',
        minFiles: value => (value && value.length >= 1) || 'Au moins 1 fichier requis',
      },

      headers: [
        { title: 'ID', key: 'id', sortable: true },
        { title: 'Format', key: 'file_type', sortable: true },
        { title: 'Fichier Source', key: 'original_file_name', sortable: true },
        { title: 'Type de Rapport', key: 'report_type', sortable: true },
        { title: 'Titre', key: 'title', sortable: true },
        { title: 'Statut', key: 'status', sortable: true },
        { title: 'Période', key: 'period', sortable: false },
        { title: 'Mentions', key: 'total_mentions', sortable: true },
        { title: 'Portée', key: 'total_reach', sortable: true },
        { title: 'Créé le', key: 'created_at', sortable: true },
        { title: 'Actions', key: 'actions', sortable: false },
      ],

      groupHeaders: [
        { title: 'ID', key: 'id', sortable: true },
        { title: 'Titre', key: 'title', sortable: true },
        { title: 'Statut', key: 'status', sortable: true },
        { title: 'Sources', key: 'source_count', sortable: false },
        { title: 'Fichiers', key: 'source_filenames', sortable: false },
        { title: 'Période', key: 'period', sortable: false },
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
    this.loadReportGroups()
    // Auto-refresh every 10 seconds
    this.refreshInterval = setInterval(() => {
      this.loadReports(true)
      this.loadReportGroups(true)
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

    async loadReportGroups(silent = false) {
      try {
        const response = await axios.get('/api/report-groups/')
        this.reportGroups = response.data.results || response.data
      } catch (error) {
        console.error('Error loading report groups:', error)
        if (!silent) {
          this.showSnackbar('Erreur lors du chargement des groupes de rapports', 'error')
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

    async uploadMultiReport() {
      if (!this.$refs.multiUploadForm.validate()) {
        return
      }

      this.uploadingMulti = true

      try {
        const formData = new FormData()
        formData.append('title', this.multiUploadData.title)

        // Add all files
        for (const file of this.multiUploadData.files) {
          formData.append('files', file)
        }

        // Add manual entry fields if provided
        if (this.multiUploadData.manual_followers) {
          formData.append('manual_followers', this.multiUploadData.manual_followers)
        }
        if (this.multiUploadData.manual_likes) {
          formData.append('manual_likes', this.multiUploadData.manual_likes)
        }
        if (this.multiUploadData.manual_shares) {
          formData.append('manual_shares', this.multiUploadData.manual_shares)
        }
        if (this.multiUploadData.manual_comments) {
          formData.append('manual_comments', this.multiUploadData.manual_comments)
        }
        if (this.multiUploadData.manual_views) {
          formData.append('manual_views', this.multiUploadData.manual_views)
        }

        await axios.post('/api/report-groups/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        this.showSnackbar(`Groupe de rapports créé avec ${this.multiUploadData.files.length} fichiers! Traitement en cours...`, 'success')

        // Reset form
        this.multiUploadData = {
          title: '',
          files: [],
          manual_followers: null,
          manual_likes: null,
          manual_shares: null,
          manual_comments: null,
          manual_views: null,
        }
        this.$refs.multiUploadForm.reset()
        this.loadReportGroups()
      } catch (error) {
        console.error('Error uploading multi-report:', error)
        this.showSnackbar('Erreur lors de la création du groupe de rapports', 'error')
      } finally {
        this.uploadingMulti = false
      }
    },

    async downloadGroupDocx(group) {
      if (group.status !== 'completed') {
        this.showSnackbar('Le rapport consolidé n\'est pas encore terminé', 'warning')
        return
      }

      try {
        const response = await axios.get(`/api/report-groups/${group.id}/download-docx/`, {
          responseType: 'blob',
        })

        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `rapport_consolide_${group.id}.docx`)
        document.body.appendChild(link)
        link.click()
        link.remove()

        this.showSnackbar('Document Word consolidé téléchargé', 'success')
      } catch (error) {
        console.error('Error downloading group DOCX:', error)
        this.showSnackbar('Erreur lors du téléchargement du document Word', 'error')
      }
    },

    async deleteReportGroup(group) {
      if (!confirm(`Êtes-vous sûr de vouloir supprimer le groupe de rapports "${group.title}" et tous ses fichiers sources?`)) {
        return
      }

      try {
        await axios.delete(`/api/report-groups/${group.id}/`)
        this.showSnackbar('Groupe de rapports supprimé', 'success')
        this.loadReportGroups()
      } catch (error) {
        console.error('Error deleting report group:', error)
        this.showSnackbar('Erreur lors de la suppression du groupe de rapports', 'error')
      }
    },

    removeFile(fileName) {
      this.multiUploadData.files = this.multiUploadData.files.filter(f => f.name !== fileName)
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

    getReportTypeColor(reportType) {
      const colors = {
        'mention_dashboard': 'blue',
        'brand24_analysis': 'green',
        'brand24_demographics': 'purple',
        'unknown': 'grey',
      }
      return colors[reportType] || 'grey'
    },

    getReportTypeIcon(reportType) {
      const icons = {
        'mention_dashboard': 'mdi-chart-bar',
        'brand24_analysis': 'mdi-chart-line',
        'brand24_demographics': 'mdi-account-group',
        'unknown': 'mdi-help-circle',
      }
      return icons[reportType] || 'mdi-file-document'
    },

    getReportTypeLabel(reportType) {
      const labels = {
        'mention_dashboard': 'Mention Dashboard',
        'brand24_analysis': 'Brand24 Analysis',
        'brand24_demographics': 'Brand24 Demographics',
        'unknown': 'Type Inconnu',
      }
      return labels[reportType] || reportType
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('fr-FR')
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
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

/* Action buttons styling */
.d-flex.ga-1 {
  gap: 8px;
}

/* Make action buttons more rounded and modern */
:deep(.v-btn--icon) {
  border-radius: 8px;
}

/* Hover effects for action buttons */
:deep(.v-btn--variant-tonal:hover) {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}

/* Data table improvements */
:deep(.v-data-table) {
  border-radius: 8px;
}

:deep(.v-data-table thead th) {
  font-weight: 600 !important;
  background-color: #f5f5f5;
}

:deep(.v-data-table tbody tr:hover) {
  background-color: #f8f9fa !important;
}
</style>
