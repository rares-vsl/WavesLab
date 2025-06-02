plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.8.0"
    id("org.danilopianini.gradle-pre-commit-git-hooks") version "2.0.24"
}

gitHooks {
    commitMsg {
        conventionalCommits()
    }
    hook("pre-commit") {
        tasks("checkstyleMain")
    }
    createHooks(true)
}


rootProject.name = "WavesLab"
