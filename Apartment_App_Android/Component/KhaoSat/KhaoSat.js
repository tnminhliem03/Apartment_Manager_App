// KhaoSat.js

import React, { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, Text, View } from "react-native";
import Api, { endpoints } from "../../Config/Api";
import styles from "./Style";

const KhaoSat = () => {
  const [surveys, setSurveys] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMoreSurveys, setLoadingMoreSurveys] = useState(false);
  const [loadingMoreQuestions, setLoadingMoreQuestions] = useState(false);
  const [loadingMoreAnswers, setLoadingMoreAnswers] = useState(false);
  const [nextSurveyPage, setNextSurveyPage] = useState(null);
  const [nextQuestionPage, setNextQuestionPage] = useState(null);
  const [nextAnswerPage, setNextAnswerPage] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const surveyRes = await Api.get(endpoints.surveys);
        setSurveys(surveyRes.data.results);
        setNextSurveyPage(surveyRes.data.next);

        const questionRes = await Api.get(endpoints.s_questions);
        setQuestions(questionRes.data.results);
        setNextQuestionPage(questionRes.data.next);

        const answerRes = await Api.get(endpoints.s_answers);
        setAnswers(answerRes.data.results);
        setNextAnswerPage(answerRes.data.next);

        setLoading(false);
      } catch (ex) {
        console.error(ex);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const loadMoreData = async (type) => {
    if (type === 'surveys' && nextSurveyPage && !loadingMoreSurveys) {
      try {
        setLoadingMoreSurveys(true);
        const res = await Api.get(nextSurveyPage);
        setSurveys([...surveys, ...res.data.results]);
        setNextSurveyPage(res.data.next);
      } catch (ex) {
        console.error("Error loading more surveys:", ex);
      } finally {
        setLoadingMoreSurveys(false);
      }
    }

    if (type === 'questions' && nextQuestionPage && !loadingMoreQuestions) {
      try {
        setLoadingMoreQuestions(true);
        const res = await Api.get(nextQuestionPage);
        setQuestions([...questions, ...res.data.results]);
        setNextQuestionPage(res.data.next);
      } catch (ex) {
        console.error("Error loading more questions:", ex);
      } finally {
        setLoadingMoreQuestions(false);
      }
    }

    if (type === 'answers' && nextAnswerPage && !loadingMoreAnswers) {
      try {
        setLoadingMoreAnswers(true);
        const res = await Api.get(nextAnswerPage);
        setAnswers([...answers, ...res.data.results]);
        setNextAnswerPage(res.data.next);
      } catch (ex) {
        console.error("Error loading more answers:", ex);
      } finally {
        setLoadingMoreAnswers(false);
      }
    }
  };

  const renderSurveyItem = ({ item }) => {
    const surveyQuestions = questions.filter(q => q.survey === item.id);
    const surveyAnswers = surveyQuestions.map(question => ({
      questionId: question.id,
      answers: answers.filter(a => a.question === question.id)
    }));

    return (
      <View style={styles.surveyContainer}>
        <Text style={styles.title}>{item.name}</Text>
        <Text style={styles.description}>{item.description}</Text>
        {surveyQuestions.map(question => (
          <View key={`q-${question.id}`} style={styles.itemContainer}>
            <Text style={styles.subtitle}>Question</Text>
            <Text style={styles.content}>{question.content}</Text>
            {surveyAnswers
              .find(sa => sa.questionId === question.id)
              .answers.map(answer => (
                <View key={`a-${answer.id}`} style={styles.answerContainer}>
                  <Text style={styles.subtitle}>Answer</Text>
                  <Text style={styles.content}>{answer.content}</Text>
                </View>
              ))}
          </View>
        ))}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Danh sách khảo sát</Text>
      {loading ? (
        <ActivityIndicator />
      ) : (
        <FlatList
          data={surveys}
          renderItem={renderSurveyItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.flatlistContent}
          onEndReached={() => loadMoreData('surveys')}
          onEndReachedThreshold={0.1}
          ListFooterComponent={loadingMoreSurveys && <ActivityIndicator />}
        />
      )}
    </View>
  );
};

export default KhaoSat;
