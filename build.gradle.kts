import io.github.andreabrighi.gradle.gitsemver.conventionalcommit.ConventionalCommit

plugins{
    id("java")
    id("checkstyle")
    alias(libs.plugins.gitSemVer)
    alias(libs.plugins.spotless)
}

buildscript {
    dependencies {
        classpath("io.github.andreabrighi:conventional-commit-strategy-for-git-sensitive-semantic-versioning-gradle-plugin:1.0.0")
    }
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }

    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

checkstyle {
    toolVersion = "10.8.0"
    configFile = file("config/checkstyle/checkstyle.xml")
}

gitSemVer {
    commitNameBasedUpdateStrategy(ConventionalCommit::semanticVersionUpdate)
    assignGitSemanticVersion()
}

spotless {
    java {
        googleJavaFormat("1.17.0")
        target("src/**/*.java")
    }
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation(platform("org.junit:junit-bom:5.10.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

tasks.withType<JavaCompile>().configureEach {
    options.compilerArgs.addAll(listOf("-Xlint:all", "-Werror"))
}

tasks.withType<Checkstyle>().configureEach {
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}


tasks.test {
    useJUnitPlatform()
}