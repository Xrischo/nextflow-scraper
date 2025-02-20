
// params for pipeline flow
params.rebuildImage = false // to rebuild the image instead of caching
params.overwrite = false // to create new tables instead of appending to them in the db
params.generateChart = false
params.chartType = ''
params.sourceTable = ''
params.columnX = ''
params.columnY = ''
params.filter = ''
params.chartName = ''

// check docker is installed
process checkAndInstallDocker {
    script:
    """
    if ! docker --version > /dev/null 2>&1; then
        apt-get update && apt-get install -y docker.io
        systemctl enable docker && systemctl start docker
    fi
    """
}

process checkAndInstallDockerBuildX {
    output:
        path "buildx.installed"

    script:
    """
    if ! docker buildx > /dev/null 2>&1; then
        apt-get install docker-buildx
        docker buildx install
    fi
    touch buildx.installed
    """
}

// check docker image exists
process checkDockerImage {
    input:
        path "buildx.installed"
        path Dockerfile
        
    output:
        path "image.built"
    script:
    """
    docker buildx build \
        ${params.rebuildImage ? '--no-cache' : ''} \
        -t $params.imageName \
        $projectDir/assets/
    touch image.built
    """
}

process csvCheckValidity {
    input:
        path csvSources

    output:
        path "sources.valid"

    script:
    """
    FILE="$csvSources"

    if [[ ! -f "\$FILE" ]]; then
        echo "Error: File not found!"
        exit 1
    fi

    # check the header
    expected_header="name,url,method,headers,selectors"
    header=\$(head -n 1 "\$FILE")
    header_trimmed=\$(echo "\$header" | sed 's/[[:space:]]*\$//')

    if [[ "\$header_trimmed" != "\$expected_header" ]]; then
        echo "Error: Invalid CSV header. \$header_trimmed \$expected_header"
        echo -n "|\$header_trimmed|"
        echo -n "|\$expected_header|"
        exit 1
    fi

    # check every row has 5 columns
    # separate by comma, after the first row, if num of fields != 5 raise error
    awk -F, 'NR>1 { if (NF != 5) { print "Error: Line " NR " has " NF " columns instead of 5"; exit 1 } }' "\$FILE"

    if [[ \$? -eq 0 ]]; then
        echo "CSV is valid"
        touch "sources.valid"
    else
        echo "CSV validation failed"
        exit 1
    fi
    """
}

process generateYamlConfig {
    publishDir params.publishDir
    container params.imageName

    input:
        path csvSources
        path "generate_yaml.py"
        path "sources.valid"
        path "docker.issetup"

    output:
        path "scraper_config.yaml"

    script:
    """
    python3 generate_yaml.py $csvSources
    """
}

process runScraper {
    publishDir params.publishDir
    container params.imageName

    input:
        path scraperYamlConfig
        path "scraper.py"

    output:
        path "scraper_data.db"

    script:
    """
    python3 scraper.py --config $scraperYamlConfig ${params.overwrite ? '--overwrite' : ''}
    """
}

process generateCharts {
    publishDir params.publishDir
    container params.imageName

    input:
        path 'scraper_data.db'
        path 'generate_chart.py'

    output:
        path 'chart.png'

    script:
    """
    python3 generate_chart.py --db scraper_data.db \
        --table $params.sourceTable \
        --chart $params.chartType \
        --x $params.columnX \
        --y $params.columnY \
        --filter "$params.filter" \
        --output $params.chartName
    """
}

workflow {
    csvSources = Channel.fromPath('assets/scraper_sources.csv')
    dockerfile = Channel.fromPath('assets/Dockerfile')
    generateYaml = Channel.fromPath('assets/generate_yaml.py')
    scraper = Channel.fromPath('assets/scraper.py')
    csvCheckValidity(csvSources)

    checkAndInstallDocker()
    checkAndInstallDockerBuildX()
    checkDockerImage(checkAndInstallDockerBuildX.out, dockerfile)
    generateYamlConfig(csvSources, generateYaml, csvCheckValidity.out, checkDockerImage.out)
    runScraper(generateYamlConfig.out, scraper)

    if (params.generateChart) {
        if (!params.chartType || !params.chartType.toLowerCase() in ['line','bar','pie']) {
            error('Chart type is required for chart generation. Please use --chartType <"line"|"bar"|"pie">')
        } else if (!params.sourceTable || params.sourceTable.size() == 0) {
            error('Source table is required for chart generation. Please use --sourceTable <table_name>')
        } else if (!params.columnX || params.columnX.size() == 0) {
            error('X axis is required for chart generation. Please use --columnX <column_name>')
        } else if (!params.columnY || params.columnY.size() == 0) {
            error('Y axis is required for chart generation. Please use --columnY <column_name>')
        } else {
            generateChartsFile = Channel.fromPath('assets/generate_chart.py')
            generateCharts(runScraper.out, generateChartsFile)
        }
    }
}